# app.py
import os
import json
import logging
import re
import time
from io import BytesIO
from flask import Flask, request, jsonify, send_from_directory
from google import genai
from flask_cors import CORS
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pdfplumber
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# -----------------------------
# NLP Setup
# -----------------------------
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

LEMMA = WordNetLemmatizer()
STOP = set(stopwords.words('portuguese')) | set(stopwords.words('english'))

# -----------------------------
# Gemini AI Setup
# -----------------------------
GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_GEMINI_API_KEY não foi encontrada.")

client = genai.Client(api_key=GEMINI_API_KEY)

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)
CORS(app)

# -----------------------------
# Funções auxiliares
# -----------------------------
def preprocess(text: str) -> str:
    try:
        tokens = nltk.word_tokenize(text.lower())
    except LookupError:
        # Fallback simples quando recursos NLTK não estão disponíveis
        tokens = [t for t in text.lower().split()]
    tokens_clean = [LEMMA.lemmatize(t) for t in tokens if t.isalpha() and t not in STOP]
    return " ".join(tokens_clean)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    out = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            out.append(page.extract_text() or "")
    return "\n".join(out)

def call_gemini_classify_and_reply(original_text: str) -> dict:
    """
    Chama o Gemini com retry exponencial para lidar com rate limits (429).
    """
    # Prompt mais explícito pedindo apenas JSON e sem comentários adicionais.
    prompt = f'''
Você é um assistente que lê um email e retorna APENAS um objeto JSON válido com estas chaves:
- category: "Produtivo" ou "Improdutivo"
- confidence: número inteiro (0-100)
- suggested_reply: string com uma resposta breve e profissional em português (3-7 linhas)

Email:
"""{original_text}"""

Retorne apenas o objeto JSON, sem explicações adicionais.
'''

    # Parâmetros de retry
    max_retries = 3
    base_delay = 1  # segundos
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )

            # o SDK pode devolver `response.text` ou outro objeto; forçamos para string
            content = getattr(response, 'text', None) or str(response)

            # tentativa direta de decodificar JSON
            try:
                parsed = json.loads(content)
                return parsed
            except Exception as parse_err:
                # tentar extrair um JSON embutido no texto do modelo
                m = re.search(r"\{.*\}", content, re.DOTALL)
                if m:
                    candidate = m.group(0)
                    try:
                        parsed = json.loads(candidate)
                        return parsed
                    except Exception:
                        pass

                # registrar resposta bruta para diagnóstico
                logging.warning("Gemini returned non-JSON response (truncated): %s", content[:2000])

                # fallback legível para o frontend (não expõe chaves)
                return {
                    "category": "Indeterminado",
                    "confidence": 0,
                    "suggested_reply": f"Não foi possível gerar resposta automática. Resposta do modelo: {content[:300]}"
                }

        except Exception as e:
            error_str = str(e)
            
            # Verificar se é erro 429 (Rate Limit / Resource Exhausted)
            is_rate_limit = "429" in error_str or "RESOURCE_EXHAUSTED" in error_str
            
            if is_rate_limit and attempt < max_retries - 1:
                # Calcular delay com backoff exponencial
                delay = base_delay * (2 ** attempt)
                logging.warning(
                    "Rate limit (429) detectado na tentativa %d. Aguardando %.1f segundos antes de retry...",
                    attempt + 1, delay
                )
                time.sleep(delay)
                continue
            
            # Se for a última tentativa ou erro diferente de 429, retornar fallback
            logging.exception("Erro ao chamar Gemini (tentativa %d/%d): %s", attempt + 1, max_retries, error_str)
            
            # Mensagem mais amigável para rate limit
            if is_rate_limit:
                return {
                    "category": "Indeterminado",
                    "confidence": 0,
                    "suggested_reply": "O serviço de IA está sobrecarregado. Tente novamente em alguns segundos."
                }
            
            return {
                "category": "Indeterminado",
                "confidence": 0,
                "suggested_reply": f"Erro ao chamar serviço de geração: {error_str[:200]}"
            }
    
    # Fallback em caso improvável de todas as tentativas falharem sem exceção
    return {
        "category": "Indeterminado",
        "confidence": 0,
        "suggested_reply": "Não foi possível processar o email após várias tentativas. Tente novamente mais tarde."
    }

# -----------------------------
# Endpoint principal
# -----------------------------
@app.route("/process", methods=["POST"])
def process_email():
    try:
        text = None

        # Arquivo enviado
        if 'file' in request.files:
            f = request.files['file']
            file_bytes = f.read()
            if f.filename.lower().endswith('.pdf') or f.content_type == 'application/pdf':
                text = extract_text_from_pdf(file_bytes)
            else:
                text = file_bytes.decode('utf-8', errors='ignore')

        # Texto colado
        else:
            text = (request.form.get('text') or "").strip()

        if not text:
            return "Nenhum texto recebido.", 400

        # Pré-processamento (opcional) - não deve bloquear a execução se falhar
        try:
            preprocessed = preprocess(text)
        except Exception:
            preprocessed = text

        # Chamada ao Gemini
        result = call_gemini_classify_and_reply(text)

        # Retorna JSON
        return jsonify(result)

    except Exception as e:
        return str(e), 500


@app.route("/", methods=["GET"])
def index():
    """Serve the frontend `public/index.html` so the user can test via browser.

    The public folder is one level up from this `api` package.
    """
    public_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
    return send_from_directory(public_dir, 'index.html')


@app.route('/<path:filename>')
def public_files(filename):
    """Serve static files from the `public` directory (css/js/assets)."""
    public_dir = os.path.join(os.path.dirname(__file__), '..', 'public')
    return send_from_directory(public_dir, filename)


@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint that does not use NLTK or Gemini — useful for smoke tests."""
    return jsonify({"ok": True, "message": "test endpoint working"}), 200

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# app.py
import os
import json
from io import BytesIO
from flask import Flask, request, jsonify
from google import genai
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import pdfplumber

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

genai.configure(api_key=GEMINI_API_KEY)

# -----------------------------
# Flask App
# -----------------------------
app = Flask(__name__)

# -----------------------------
# Funções auxiliares
# -----------------------------
def preprocess(text: str) -> str:
    tokens = nltk.word_tokenize(text.lower())
    tokens_clean = [LEMMA.lemmatize(t) for t in tokens if t.isalpha() and t not in STOP]
    return " ".join(tokens_clean)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    out = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            out.append(page.extract_text() or "")
    return "\n".join(out)

def call_gemini_classify_and_reply(original_text: str) -> dict:
    prompt = f"""
Você é um assistente que lê um email e retorna um JSON com:
- category: "Produtivo" ou "Improdutivo"
- confidence: uma porcentagem de 0 a 100
- suggested_reply: uma resposta breve e profissional em português (3-7 linhas), adequada à categoria.

Email:
\"\"\"{original_text}\"\"\"

Retorne apenas o objeto JSON.
"""
    try:
        response = genai.ChatCompletion.create(
            model="gemini-2.5-flash",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_output_tokens=512
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        # fallback em caso de JSON inválido
        return {
            "category": "Produtivo",
            "confidence": 80,
            "suggested_reply": f"Não foi possível gerar resposta automática: {str(e)}"
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

        # Pré-processamento (opcional)
        preprocessed = preprocess(text)

        # Chamada ao Gemini
        result = call_gemini_classify_and_reply(text)

        # Retorna JSON
        return jsonify(result)

    except Exception as e:
        return str(e), 500

# -----------------------------
# Run Flask
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

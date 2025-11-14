# api/process.py
import os
import json
from typing import Tuple
from io import BytesIO

from vercel_sdk import VercelRequest, VercelResponse  # se não, Vercel espera handler(request)
# Se o runtime Vercel usa o padrão WSGI/simple, adaptar (abaixo tem fallback)

# Google GenAI SDK
from google import genai

# NLP
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# PDF parsing
import pdfplumber

# Ensure nltk resources (first deploy pode demorar — considerar pré-empacotar ou usar lightweight rules)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

LEMMA = WordNetLemmatizer()
STOP = set(stopwords.words('portuguese')) | set(stopwords.words('english'))

# init gemini client using API key from env
genai.configure(api_key=os.environ.get("GOOGLE_GEMINI_API_KEY"))

def preprocess(text: str) -> str:
    # simples: lower, tokenize, remove stopwords, lemmatize
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
    # Prompt design: pedir ao modelo 1) categoria 2) resposta pronta
    prompt = f"""
You are an assistant that reads an incoming email and outputs JSON with:
- category: either "Produtivo" or "Improdutivo"
- confidence: a percentage 0-100
- suggested_reply: a brief professional reply in Portuguese (3-7 lines), suitable for the category.

Email:
\"\"\"{original_text}\"\"\"
Return ONLY a JSON object.
"""
    # Use a chat or generation API
    response = genai.ChatCompletion.create(
        model="gemini-2.5-flash",  # ajustar conforme disponibilidade (ex.: gemini-pro, gemini-1.5)
        messages=[{"role":"user","content":prompt}],
        temperature=0.0,
        max_output_tokens=512
    )
    # parse
    content = response.choices[0].message.content
    try:
        parsed = json.loads(content)
    except Exception:
        # fallback: tentar extrair manualmente
        parsed = {"category":"Produtivo","confidence":80,"suggested_reply":content}
    return parsed

# Vercel handler compatibility: Vercel's python runtime expects a function named "handler"
def handler(request):
    try:
        # request.files or request.form depending on runtime
        text = None
        if request.files and 'file' in request.files:
            f = request.files['file']
            file_bytes = f.read()
            # basic pdf detection:
            if f.filename.lower().endswith('.pdf') or f.content_type == 'application/pdf':
                text = extract_text_from_pdf(file_bytes)
            else:
                text = file_bytes.decode('utf-8', errors='ignore')
        else:
            text = (request.form.get('text') or request.body.decode('utf-8') or "").strip()

        if not text:
            return VercelResponse("Nenhum texto recebido.", status=400)

        # preprocess (optional)
        pre = preprocess(text)

        # call Gemini to classify + generate reply
        parsed = call_gemini_classify_and_reply(text)

        return VercelResponse(json.dumps(parsed), headers={"Content-Type": "application/json"})
    except Exception as e:
        return VercelResponse(str(e), status=500)

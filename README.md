# Email Classifier

Projeto simples que classifica emails como **Produtivo** ou **Improdutivo** e sugere uma resposta automática.

Veja os passos rápidos para rodar localmente e instruções para deploy no Render.

**Requisitos**
- Python 3.10+
- Conta e chave de API para a API do Google Gemini (defina a variável `GOOGLE_GEMINI_API_KEY`).

## Rodando localmente

1. Crie e ative um virtualenv (PowerShell):

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
```

2. Instale dependências:

```powershell
pip install -r requirements.txt
```

3. Crie um arquivo `.env` na raiz com sua chave (exemplo):

```
GOOGLE_GEMINI_API_KEY=YOUR_API_KEY_HERE
```

4. Execute a aplicação:

```powershell
python api/app.py
```

5. Abra o navegador em `http://localhost:5000` e teste o envio de `.txt`/`.pdf` ou cole um email.

## Deploy no Render

1. Crie um novo serviço Web no Render (Public repo ou linked).
2. Configure `Start Command` como:

```
gunicorn api.app:app --bind 0.0.0.0:$PORT
```

3. Adicione a variável de ambiente `GOOGLE_GEMINI_API_KEY` nas configurações do serviço.
4. Faça deploy e acesse a URL fornecida pelo Render.

## Observações
- O backend usa a API do Gemini para classificação e geração de respostas; a aplicação também faz pré-processamento simples com NLTK.
- Se desejar treino local ou um classificador próprio (sem usar Gemini), posso ajudar a adicionar um pipeline com scikit-learn.

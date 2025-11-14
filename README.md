# Email Classifier

Um projeto simples para classificar e sugerir respostas automáticas a e-mails usando um modelo de IA (Google Gemini) e um backend em Python (Serverless — Vercel).

Resumo
- Classifica e-mails como "Produtivo" ou "Improdutivo".
- Gera uma resposta sugerida em português.
- Interface web leve em `public/index.html` e backend em `api/process.py`.

Links importantes
- Deploy (substitua pelo seu): https://SEU-LINK-VERCEL-AQUI.vercel.app
- Repositório: https://github.com/WanDall2104/email-classifier.git

Funcionalidades
- Upload de arquivos `.txt` e `.pdf`, ou colar o texto manualmente.
- Pré-processamento simples (stopwords + lematização).
- Chamada ao Google Gemini para classificação e geração de resposta.

Estrutura do projeto

```
email-classifier/
├── api/
│   └── process.py        # Função serverless (Python)
├── public/
│   ├── index.html        # Interface web
│   ├── css/
│   │   └── styles.css    # Estilos da interface
│   └── js/
│       └── main.js       # Código JS da interface (organizado)
├── example_emails/       # Exemplos de e-mails (produtivo/improdutivo)
├── requirements.txt
└── README.md
```

Pré-requisitos
- Python 3.8+
- pip
- (Opcional) Node.js + Vercel CLI para rodar o ambiente serverless localmente

Dependências principais
As dependências declaradas em `requirements.txt` atualmente são:

- google-genai >= 0.9.0
- nltk >= 3.8
- pdfplumber >= 0.7
- vercel-sdk >= 0.1  # pode ser desnecessário dependendo do runtime

Instalação e execução local (Windows - PowerShell)

1) Clone o repositório

```powershell
git clone https://github.com/SEU-USUARIO/email-classifier
cd "email-classifier"
```

2) Crie e ative um ambiente virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell
```

3) Instale as dependências

```powershell
pip install -r requirements.txt
```

4) Configure a chave da API (variável de ambiente)

```powershell
$env:GOOGLE_GEMINI_API_KEY = "SUA_CHAVE_AQUI"
```

5) Rodando localmente com Vercel (opcional)

Se preferir testar a função serverless localmente, instale o Vercel CLI e execute `vercel dev`.

```powershell
npm i -g vercel
vercel dev
# A interface ficará em http://localhost:3000
```

Observação: A função em `api/process.py` espera receber o texto do e-mail (ou o arquivo .pdf/.txt). Ela realiza extração, pré-processamento e chama o modelo para obter a classificação e a sugestão de resposta.

Como usar
- Abra a interface `public/index.html` no navegador (quando executado via Vercel, acessível em `/`).
- Faça upload do arquivo ou cole o texto.
- O backend retornará um JSON com: categoria (Produtivo/Improdutivo), confiança (0–100) e resposta sugerida.

Boas práticas / Notas
- Substitua os links e o nome de usuário do GitHub nos exemplos acima antes do deploy público.
- Garanta que a chave `GOOGLE_GEMINI_API_KEY` esteja configurada na Vercel para deploy.
- O pacote `vercel-sdk` é opcional — você pode não precisar dele dependendo do ambiente de execução.

Contribuições
- Sugestões, correções e PRs são bem-vindos. Abra uma issue antes de PRs maiores para alinharmos a implementação.

Contato
- Autor: Gabriel Wan Dall Parra

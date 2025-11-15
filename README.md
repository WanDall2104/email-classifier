# Email Classifier

🔗 **Acesse o projeto online:**  
https://email-classifier-3cwc.onrender.com

Uma aplicação web que utiliza Inteligência Artificial para **classificar** e **responder automaticamente** e‑mails recebidos por uma empresa que lida com alto volume diário de mensagens.

---

## 🧠 Visão Geral

Este projeto permite que você envie o conteúdo de um e‑mail (ou arraste/cole em `.txt` ou `.pdf`) e a aplicação:

- Classifique o e‑mail como **Produtivo** ou **Impro­dutivo**.
- Sugira uma resposta automática com base na classificação e no conteúdo do e‑mail.
- Tudo isso por meio da API generativa da Generative Language API (versão do Google Gemini API) do Google Cloud, combinada com um front‑end simples.

---

## 🚀 Tecnologias

- Linguagem: **Python 3.10+**
- Framework Web: Flask
- Biblioteca de pré‑processamento: NLTK
- Modelo LLM: Google Gemini via Generative Language API
- Hospedagem: Render
- Front‑end: HTML + CSS + Javascript
- Arquitetura: Separação de frontend/public + backend/api

---

## 📁 Estrutura do Projeto

```
/email‑classifier
│
├── api/                   
│   └── app.py             
│
├── example_emails/        
│
├── public/                
│   └── index.html         
│
├── .env.example           
├── requirements.txt       
└── README.md              
```

---

## 🧰 Como Rodar Localmente

## Aviso sobre licença:
As instruções abaixo destinam-se apenas a uso pessoal, interno ou para fins de avaliação.
A execução deste software não concede permissão para redistribuição, modificação, publicação ou uso comercial conforme definido na Licença Proprietária deste projeto.

1. Clone o repositório:
   ```bash
   git clone https://github.com/WanDall2104/email‑classifier.git
   cd email-classifier
   ```

2. Crie e ative um virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   # ou
   .\.venv\Scripts\Activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz com sua chave da Google Gemini API:
   ```env
   GOOGLE_GEMINI_API_KEY=YOUR_API_KEY_HERE
   ```

5. Execute a aplicação:
   ```bash
   python api/app.py
   ```

6. Abra `http://localhost:5000`.

---

## ☁️ Deploy no Render

1. Crie um novo Web Service no Render.
2. Configure o comando:
   ```bash
   gunicorn api.app:app --bind 0.0.0.0:$PORT
   ```
3. Adicione variáveis de ambiente:
   ```
   GOOGLE_GEMINI_API_KEY = <sua_api_key_aqui>
   ```

---

## 🎯 Próximos Passos

- Suporte a mais formatos de arquivo.
- Dashboard de métricas.
- Integração com Gmail/Outlook.
- Aprendizado contínuo.
- Suporte multilíngue.

---

## ✉️ Contato

Desenvolvido por **Gabriel Wan Dall Parra**. 
🔗 LinkedIn: https://www.linkedin.com/in/seu-usuario-aqui

---

## 📝 Licença

Este projeto está licenciado sob uma **Licença Proprietária**.  
Todos os direitos são reservados.  
O uso, cópia, modificação ou distribuição deste código só é permitido mediante autorização explícita do autor.


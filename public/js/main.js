const submitBtn = document.getElementById("submitBtn");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");
const textInput = document.getElementById("textInput");
const resultDiv = document.getElementById("resultDiv");
const resultText = document.getElementById("resultText");
const errorDiv = document.getElementById("errorDiv");
const errorText = document.getElementById("errorText");
const categorySpan = document.getElementById("categorySpan");
const confidenceSpan = document.getElementById("confidenceSpan");
const suggestedReply = document.getElementById("suggestedReply");
const copyReplyBtn = document.getElementById("copyReplyBtn");

async function sendForm() {
    resultDiv.style.display = "none";
    errorDiv.style.display = "none";
    resultText.textContent = '';
    categorySpan.textContent = '';
    confidenceSpan.textContent = '';
    suggestedReply.textContent = '';

    const formData = new FormData();

    if (fileInput.files.length > 0) {
        formData.append("file", fileInput.files[0]);
    } else if (textInput.value.trim() !== "") {
        formData.append("text", textInput.value.trim());
    } else {
        errorText.textContent = "Por favor, insira um texto ou selecione um arquivo.";
        errorDiv.style.display = "block";
        return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Processando...";

    try {
        const response = await fetch("/process", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const text = await response.text();
            throw new Error(text || `HTTP ${response.status}`);
        }

        const data = await response.json();

        // Tentar preencher campos conhecidos
        categorySpan.textContent = data.category || data.category_label || '—';
        confidenceSpan.textContent = (data.confidence !== undefined) ? `${data.confidence}%` : (data.confidence_score || '—');
        suggestedReply.textContent = data.suggested_reply || data.suggestedReply || data.suggestedReplyText || '';

        resultText.textContent = JSON.stringify(data, null, 2);
        resultDiv.style.display = "block";

    } catch (err) {
        errorText.textContent = "Erro: " + err.message;
        errorDiv.style.display = "block";
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Processar Email";
    }
}

submitBtn.addEventListener('click', sendForm);

copyReplyBtn.addEventListener('click', async () => {
    const text = suggestedReply.textContent || resultText.textContent;
    if (!text) return;
    try {
        await navigator.clipboard.writeText(text);
        copyReplyBtn.textContent = 'Copiado!';
        setTimeout(() => { copyReplyBtn.textContent = 'Copiar Resposta'; }, 1500);
    } catch (e) {
        console.warn('Clipboard failed', e);
    }
});

// Atualiza o nome do arquivo selecionado
if (fileInput) {
  fileInput.addEventListener("change", () => {
    fileName.textContent = fileInput.files.length
      ? fileInput.files[0].name
      : "Nenhum arquivo selecionado";
  });
}
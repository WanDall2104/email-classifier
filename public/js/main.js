// ==============================
// Referências do DOM
// ==============================
const UI = {
    submitBtn: document.getElementById("submitBtn"),
    fileInput: document.getElementById("fileInput"),
    fileName: document.getElementById("fileName"),
    textInput: document.getElementById("textInput"),

    result: document.getElementById("resultDiv"),
    error: document.getElementById("errorDiv"),
    errorText: document.getElementById("errorText"),

    category: document.getElementById("categorySpan"),
    confidence: document.getElementById("confidenceSpan"),
    reply: document.getElementById("suggestedReply"),
    copyReplyBtn: document.getElementById("copyReplyBtn")
};

// ==============================
// Funções utilitárias
// ==============================
function clearUI() {
    UI.result.style.display = "none";
    UI.error.style.display = "none";
    UI.category.textContent = "";
    UI.confidence.textContent = "";
    UI.reply.textContent = "";
}

function showError(message) {
    UI.errorText.textContent = message;
    UI.error.style.display = "block";
}

function toggleSubmitButton(isProcessing) {
    UI.submitBtn.disabled = isProcessing;
    UI.submitBtn.textContent = isProcessing ? "Processando..." : "Processar Email";
}

function buildFormData() {
    const formData = new FormData();

    if (UI.fileInput.files.length > 0) {
        formData.append("file", UI.fileInput.files[0]);
    } else if (UI.textInput.value.trim() !== "") {
        formData.append("text", UI.textInput.value.trim());
    }

    return formData;
}

// ==============================
// Envio do formulário
// ==============================
async function sendForm() {
    clearUI();

    const formData = buildFormData();
    if (!formData.has("file") && !formData.has("text")) {
        showError("Por favor, insira um texto ou selecione um arquivo.");
        return;
    }

    toggleSubmitButton(true);

    try {
        const response = await fetch("/process", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const serverMessage = await response.text();
            throw new Error(serverMessage || `HTTP ${response.status}`);
        }

        const data = await response.json();

        // Preenche campos retornados pela API
        UI.category.textContent =
            data.category ?? data.category_label ?? "—";

        UI.confidence.textContent =
            data.confidence !== undefined
                ? `${data.confidence}%`
                : (data.confidence_score ?? "—");

        UI.reply.textContent =
            data.suggested_reply ??
            data.suggestedReply ??
            data.suggestedReplyText ??
            "";

        UI.result.style.display = "block";

    } catch (err) {
        showError("Erro: " + err.message);
    } finally {
        toggleSubmitButton(false);
    }
}

// ==============================
// Eventos
// ==============================
UI.submitBtn.addEventListener("click", (e) => {
    e.preventDefault();
    sendForm();
});

UI.copyReplyBtn.addEventListener("click", async () => {
    const text = UI.reply.textContent;
    if (!text) return;

    try {
        await navigator.clipboard.writeText(text);
        UI.copyReplyBtn.textContent = "Copiado!";
        setTimeout(() => {
            UI.copyReplyBtn.textContent = "Copiar Resposta";
        }, 1500);
    } catch (err) {
        console.warn("Clipboard failed", err);
    }
});

// Atualizar nome do arquivo selecionado e controlar textarea
if (UI.fileInput) {
    UI.fileInput.addEventListener("change", () => {
        UI.fileName.textContent =
            UI.fileInput.files.length
                ? UI.fileInput.files[0].name
                : "Nenhum arquivo selecionado";
        
        // Desabilitar textarea quando arquivo é selecionado
        UI.textInput.disabled = UI.fileInput.files.length > 0;
        if (UI.fileInput.files.length > 0) {
            UI.textInput.value = "";
        }
    });
}

// Controlar arquivo quando texto é digitado
if (UI.textInput) {
    UI.textInput.addEventListener("input", () => {
        // Desabilitar input de arquivo quando texto é digitado
        UI.fileInput.disabled = UI.textInput.value.trim().length > 0;
        if (UI.textInput.value.trim().length > 0) {
            UI.fileInput.value = "";
            UI.fileName.textContent = "Nenhum arquivo selecionado";
        }
    });
}

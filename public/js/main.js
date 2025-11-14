const submitBtn = document.getElementById("submitBtn");
const fileInput = document.getElementById("fileInput");
const textInput = document.getElementById("textInput");
const resultDiv = document.getElementById("resultDiv");
const resultText = document.getElementById("resultText");
const errorDiv = document.getElementById("errorDiv");
const errorText = document.getElementById("errorText");

    submitBtn.addEventListener("click", async () => {
        resultDiv.style.display = "none";
        errorDiv.style.display = "none";

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

            try {
                const response = await fetch("/process", {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    const text = await response.text();
                    throw new Error(text);
                }

                const data = await response.json();
                resultText.textContent = JSON.stringify(data, null, 2);
                resultDiv.style.display = "block";
            } catch (err) {
                errorText.textContent = "Erro: " + err.message;
                errorDiv.style.display = "block";
            }
        });
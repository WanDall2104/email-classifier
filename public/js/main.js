// Código reorganizado para Email Classifier
(() => {
    const fileInput = document.getElementById('file')
    const textArea = document.getElementById('text')
    const resultEl = document.getElementById('result')
    const sendBtn = document.getElementById('send')
    const spinner = document.querySelector('.spinner')

    function setBusy(busy){
        sendBtn.disabled = busy
        sendBtn.textContent = busy ? 'Processando…' : 'Processar'
        if(spinner){
            // spinner uses the boolean hidden attribute in the HTML
            spinner.hidden = !busy
            spinner.setAttribute('aria-hidden', String(!busy))
        }
    }

    function escapeHTML(str){
        if(str == null) return ''
        return String(str).replace(/[&<>"']/g, s => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[s]))
    }

    function showError(msg){
        resultEl.innerHTML = ''
        const el = document.createElement('div')
        el.style.color = 'crimson'
        el.textContent = msg
        resultEl.appendChild(el)
    }

    function showResult(data){
        resultEl.innerHTML = ''
        const wrap = document.createElement('div')
        wrap.style.marginTop = '10px'

        const cat = document.createElement('div')
        cat.innerHTML = `<strong>Categoria:</strong> ${escapeHTML(data.category)}`
        wrap.appendChild(cat)

        const conf = document.createElement('div')
        conf.innerHTML = `<strong>Confiança:</strong> ${data.confidence ?? '—'}`
        wrap.appendChild(conf)

        const label = document.createElement('div')
        label.innerHTML = `<strong>Resposta sugerida:</strong>`
        wrap.appendChild(label)

        const pre = document.createElement('pre')
        pre.style.background = '#f6f8fa'
        pre.style.padding = '10px'
        pre.style.borderRadius = '8px'
        pre.textContent = data.suggested_reply || ''
        wrap.appendChild(pre)

        resultEl.appendChild(wrap)
    }

    function validateInput(file, text){
        if(file) return true
        if(text && text.trim().length > 0) return true
        return false
    }

    async function handleClick(){
        const file = fileInput.files[0]
        const text = textArea.value || ''

        if(!validateInput(file, text)){
            showError('Por favor, envie um arquivo (.txt/.pdf) ou cole o texto do e-mail.')
            return
        }

        setBusy(true)
        resultEl.innerHTML = '<em>Processando…</em>'

        const body = new FormData()
        if(file){
            body.append('file', file)
        } else {
            body.append('text', text)
        }

        try {
            const res = await fetch('/api/process', { method: 'POST', body })
            if(!res.ok){
                const errText = await res.text()
                showError('Erro: ' + errText)
                return
            }
            const data = await res.json()
            showResult(data)
        } catch (err){
            showError('Erro inesperado: ' + (err && err.message ? err.message : String(err)))
        } finally {
            setBusy(false)
        }
    }

    sendBtn.addEventListener('click', handleClick)
})()

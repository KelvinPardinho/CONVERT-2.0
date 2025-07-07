// =========================================================================
// static/js/main.js (VERSÃO FINAL, COMPLETA E CORRIGIDA)
// =========================================================================

// --- 1. FUNÇÕES GLOBAIS E DE UTILIDADE ---

/**
 * Inicializa o botão de alternância de tema (Dark/Light Mode).
 */
function initializeThemeToggle() {
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    if (!themeToggleButton || !themeIcon) return;

    const applyTheme = (theme) => {
        document.body.classList.toggle('dark-mode', theme === 'dark');
        themeIcon.classList.toggle('fa-sun', theme === 'dark');
        themeIcon.classList.toggle('fa-moon', theme !== 'dark');
    };

    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    applyTheme(initialTheme);

    themeToggleButton.addEventListener('click', () => {
        const newTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    });
}

/**
 * Obtém o valor de um cookie. Essencial para o CSRF token do Django.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// --- 2. LÓGICA PRINCIPAL DA APLICAÇÃO ---

document.addEventListener('DOMContentLoaded', function() {
    
    initializeThemeToggle();
    const csrftoken = getCookie('csrftoken');

    let selectedTool = null;
    let uploadedFile = null;
    let toolState = {
        merge: { files: [], rotations: {} },
        split: { selections: [], rotations: [] },
        image: { rotations: [] },
        convertImage: { rotation: 0 }
    };

    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!fileInput.files.length) return alert('Por favor, selecione um arquivo PDF.');
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnHTML = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Validando...';
            submitBtn.disabled = true;
            
            fetch('/api/upload/', { method: 'POST', body: formData, headers: { 'X-CSRFToken': csrftoken } })
            .then(response => response.ok ? response.json() : response.json().then(err => { throw new Error(err.message || 'Erro no servidor') }))
            .then(data => {
                if (data.success) {
                    uploadedFile = { name: data.filename, numPages: data.num_pages, file: fileInput.files[0] };
                    submitBtn.innerHTML = '<i class="fas fa-check me-2"></i>Arquivo Carregado!';
                    submitBtn.classList.replace('btn-primary', 'btn-success');
                    
                    const alertEl = document.createElement('div');
                    alertEl.className = 'alert alert-success mt-3';
                    alertEl.innerHTML = `<i class="fas fa-check-circle me-2"></i>Arquivo <strong>${data.filename}</strong> (${data.num_pages || 'N/A'} páginas) pronto! Escolha uma ferramenta.`;
                    
                    const existingAlert = uploadForm.querySelector('.alert');
                    if (existingAlert) existingAlert.remove();
                    uploadForm.appendChild(alertEl);
                } else {
                    throw new Error(data.message || 'Erro ao processar o arquivo.');
                }
            })
            .catch(error => {
                alert(error.message);
                submitBtn.innerHTML = originalBtnHTML;
                submitBtn.disabled = false;
            });
        });
    }

    document.querySelectorAll('.tool-select-btn').forEach(button => {
        button.addEventListener('click', () => {
            const tool = button.dataset.tool;
            if (tool) openToolModal(tool);
        });
    });

    function openToolModal(tool) {
        if (!uploadedFile && !['merge', 'image-to-pdf', 'convert-image'].includes(tool)) {
            return alert('Para usar esta ferramenta, por favor, carregue um arquivo PDF na seção "Fazer Upload do PDF" primeiro.');
        }
        selectedTool = tool;

        const toolConfigs = {
            'merge': { title: 'Unir PDFs', body: `<div class="mb-3"><label for="tool-input" class="form-label">Selecione dois ou mais arquivos PDF:</label><input type="file" id="tool-input" class="form-control" multiple accept=".pdf"></div><div id="previewContainer" class="row g-3"><p class="text-muted text-center">Nenhum arquivo selecionado.</p></div>` },
            'split': { title: 'Dividir PDF', body: `<div class="row border-bottom pb-3 mb-3"><div class="col-md-7"><h6>Modo de Divisão</h6><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitIndividual" value="individual" checked><label class="form-check-label" for="splitIndividual">Extrair páginas selecionadas (.zip)</label></div><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitMerge" value="merge"><label class="form-check-label" for="splitMerge">Unir páginas selecionadas</label></div><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitPairs" value="pairs"><label class="form-check-label" for="splitPairs">Dividir em pares</label></div></div><div class="col-md-5 d-flex align-items-center justify-content-end"><div id="split-selection-controls" class="form-check me-3"><input class="form-check-input" type="checkbox" id="selectAllPages"><label class="form-check-label" for="selectAllPages">Selecionar Todas</label></div><button class="btn btn-secondary" id="rotateAllBtn"><i class="fas fa-sync-alt me-2"></i>Girar Todas</button></div></div><div id="previewContainer" class="row g-3 text-center"><div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Carregando...</div></div>` },
            'compress': { title: 'Comprimir PDF', body: `<div class="mb-3"><label for="compressionLevel" class="form-label">Nível de Compressão:</label><select id="compressionLevel" class="form-select"><option value="low">Baixa (Melhor Qualidade)</option><option value="medium" selected>Média (Equilibrado)</option><option value="high">Alta (Menor Tamanho)</option></select></div>` },
            'protect': { title: 'Proteger PDF', body: `<div class="mb-3"><label for="protectPassword" class="form-label">Defina uma senha:</label><input type="password" id="protectPassword" class="form-control" required></div><div class="mb-3"><label for="confirmPassword" class="form-label">Confirme a senha:</label><input type="password" id="confirmPassword" class="form-control" required></div>` },
            'unlock': { title: 'Remover Senha', body: `<div class="mb-3"><label for="unlockPassword" class="form-label">Digite a senha atual:</label><input type="password" id="unlockPassword" class="form-control" required></div>` },
            'pdf-to-word': { title: 'PDF para Word', body: `<p>O arquivo carregado (<strong>${uploadedFile?.name || 'PDF'}</strong>) será convertido. Clique em processar.</p>` },
        };
        
        const modalEl = document.getElementById('toolModal');
        const modalTitle = document.getElementById('toolModalTitle');
        const modalBody = document.getElementById('toolModalBody');
        const config = toolConfigs[tool] || { title: `Ferramenta: ${tool.replace(/-/g, ' ')}`, body: `<p>Clique em processar para continuar.</p>` };
        modalTitle.textContent = config.title;
        modalBody.innerHTML = config.body;
        bootstrap.Modal.getOrCreateInstance(modalEl).show();

        if (tool === 'split') {
            toolState.split = { selections: [], rotations: [] };
            renderPagePreview(uploadedFile.file, 'split', uploadedFile);
            document.getElementById('selectAllPages').addEventListener('change', (e) => App.toggleAllSelections(e.target.checked));
            document.getElementById('rotateAllBtn').addEventListener('click', () => App.rotateAllPreviews());
        }
    }

    function renderPagePreview(file, mode, uploadedFileInfo) {
        const previewContainer = document.getElementById('previewContainer');
        if (!file || !uploadedFileInfo || !uploadedFileInfo.numPages) { 
            previewContainer.innerHTML = `<div class="alert alert-danger">Não foi possível carregar a pré-visualização.</div>`;
            return;
        }
        const numPages = uploadedFileInfo.numPages;
        previewContainer.innerHTML = `<div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Renderizando ${numPages} páginas...</div>`;

        const fileReader = new FileReader();
        fileReader.onload = (e) => {
            pdfjsLib.getDocument({ data: e.target.result }).promise.then(pdf => {
                previewContainer.innerHTML = '';
                if (mode === 'split') toolState.split = { selections: Array(numPages).fill(false), rotations: Array(numPages).fill(0) };
                
                for (let i = 1; i <= numPages; i++) {
                    pdf.getPage(i).then(page => {
                        const canvas = document.createElement('canvas');
                        const scale = 0.3;
                        const viewport = page.getViewport({ scale });
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        page.render({ canvasContext: canvas.getContext('2d'), viewport: viewport });

                        const cardHTML = `
                            <div class="col-xl-2 col-lg-3 col-md-4 col-sm-6">
                                <div class="card h-100">
                                    <div class="card-body p-2 d-flex flex-column align-items-center">
                                        <div class="form-check d-flex align-items-center justify-content-center mb-2">
                                            <input class="form-check-input mt-0" type="checkbox" id="page-checkbox-${i-1}" onchange="App.togglePageSelection(${i-1})">
                                            <label class="form-check-label ms-2 small" for="page-checkbox-${i-1}">Página ${i}</label>
                                        </div>
                                        <div id="page-canvas-wrapper-${i-1}" class="my-1" style="transition: transform 0.3s ease;"></div>
                                        <button class="btn btn-outline-secondary btn-sm" onclick="App.rotatePagePreview(${i-1})"><i class="fas fa-sync-alt"></i> Girar</button>
                                    </div>
                                </div>
                            </div>`;
                        previewContainer.insertAdjacentHTML('beforeend', cardHTML);
                        document.getElementById(`page-canvas-wrapper-${i-1}`).appendChild(canvas);
                    });
                }
            });
        };
        fileReader.readAsArrayBuffer(file);
    }

    const processButton = document.getElementById('processTool');
    if (processButton) {
        processButton.addEventListener('click', function() {
            const button = this;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
            button.disabled = true;

            processSelectedTool()
                .then(result => {
                    if (result.success) {
                        bootstrap.Modal.getInstance(document.getElementById('toolModal')).hide();
                        showResults(result);
                    } else {
                        throw new Error(result.message || 'Ocorreu um erro no servidor.');
                    }
                })
                .catch(error => alert(`Erro: ${error.message}`))
                .finally(() => {
                    button.innerHTML = 'Processar';
                    button.disabled = false;
                });
        });
    }

    async function processSelectedTool() {
        const formData = new FormData();
        formData.append('file', uploadedFile.file);

        switch (selectedTool) {
            case 'split':
                if (toolState.split.selections.every(s => !s)) throw new Error('Nenhuma página foi selecionada.');
                formData.append('split_mode', document.querySelector('input[name="splitMode"]:checked').value);
                formData.append('selections', JSON.stringify(toolState.split.selections));
                formData.append('rotations', JSON.stringify(toolState.split.rotations));
                break;
            case 'compress':
                formData.append('compression_level', document.getElementById('compressionLevel').value);
                break;
            case 'protect':
                const password = document.getElementById('protectPassword').value;
                const confirm = document.getElementById('confirmPassword').value;
                if (!password) throw new Error('O campo de senha não pode estar vazio.');
                if (password !== confirm) throw new Error('As senhas não coincidem.');
                formData.append('password', password);
                break;
        }
        
        return fetch(`/api/${selectedTool}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrftoken },
            body: formData
        }).then(response => response.ok ? response.json() : response.json().then(err => { throw new Error(err.message || 'Erro desconhecido') }));
    }

    function showResults(result) {
        const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('resultsModal'));
        const modalBody = document.getElementById('resultsModalBody');
        let content = `<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i>${result.message}</div>`;
        if (result.download_url) {
            content += `<div class="text-center mb-3"><a href="${result.download_url}" class="btn btn-primary btn-lg" download><i class="fas fa-download me-2"></i>Baixar Arquivo</a></div>`;
        }
        modalBody.innerHTML = content;
        modal.show();
    }
});

// --- 3. NAMESPACE GLOBAL PARA FUNÇÕES DE UI ACESSÍVEIS VIA ONCLICK ---
window.App = {
    rotatePagePreview: function(pageIndex) {
        const state = toolState.split; // Simplificado para split, adapte se usar em outras ferramentas
        if (!state || !state.rotations) return;
        state.rotations[pageIndex] = (state.rotations[pageIndex] + 90) % 360;
        const wrapper = document.getElementById(`page-canvas-wrapper-${pageIndex}`);
        if (wrapper) wrapper.style.transform = `rotate(${state.rotations[pageIndex]}deg)`;
    },
    togglePageSelection: function(pageIndex) {
        toolState.split.selections[pageIndex] = !toolState.split.selections[pageIndex];
        const selectAllCheckbox = document.getElementById('selectAllPages');
        if (!selectAllCheckbox) return;
        selectAllCheckbox.checked = toolState.split.selections.every(s => s);
    },
    toggleAllSelections: function(isChecked) {
        if (!toolState.split.selections) return;
        toolState.split.selections.fill(isChecked);
        for (let i = 0; i < toolState.split.selections.length; i++) {
            const checkbox = document.getElementById(`page-checkbox-${i}`);
            if (checkbox) checkbox.checked = isChecked;
        }
    },
    rotateAllPreviews: function() {
        if (!toolState.split.rotations) return;
        for (let i = 0; i < toolState.split.rotations.length; i++) {
            this.rotatePagePreview(i);
        }
    }
};
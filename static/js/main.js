// =========================================================================
// static/js/main.js (VERSÃO FINAL, COMPLETA E CORRIGIDA)
// =========================================================================

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

document.addEventListener('DOMContentLoaded', function() {
    
    const csrftoken = getCookie('csrftoken');
    let selectedTool = null;
    let uploadedFile = null;
    let toolState = {
        split: { selections: [], rotations: [] },
    };

    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!fileInput.files.length) return alert('Por favor, selecione um arquivo PDF.');
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
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
                } else { throw new Error(data.message || 'Erro ao processar o arquivo.'); }
            })
            .catch(error => {
                alert(error.message);
                submitBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Enviar Arquivo';
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
        const needsUpload = !['merge', 'image-to-pdf', 'convert-image'].includes(tool);
        if (needsUpload && !uploadedFile) {
            return alert('Para usar esta ferramenta, por favor, carregue um arquivo PDF primeiro.');
        }
        selectedTool = tool;

        // CORREÇÃO 1: Adicionado o atributo 'for' nas labels para que o clique funcione.
        const toolConfigs = {
            'split': { title: 'Dividir PDF', body: `<div class="row border-bottom pb-3 mb-3"><div class="col-md-7"><h6>Modo de Divisão</h6><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitIndividual" value="individual" checked><label class="form-check-label" for="splitIndividual">Extrair páginas selecionadas (.zip)</label></div><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitMerge" value="merge"><label class="form-check-label" for="splitMerge">Unir páginas selecionadas</label></div><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitPairs" value="pairs"><label class="form-check-label" for="splitPairs">Dividir em pares</label></div></div><div class="col-md-5 d-flex align-items-center justify-content-end" id="splitPageControls"><div class="form-check me-3"><input class="form-check-input" type="checkbox" id="selectAllPages"><label class="form-check-label" for="selectAllPages">Selecionar Todas</label></div><button class="btn btn-secondary" id="rotateAllBtn"><i class="fas fa-sync-alt me-2"></i>Girar Todas</button></div></div><div id="previewContainer" class="row g-3 text-center"><div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Carregando...</div></div>` },
            'compress': { title: 'Comprimir PDF', body: `<div class="mb-3"><label for="compressionLevel" class="form-label">Nível de Compressão:</label><select id="compressionLevel" class="form-select"><option value="low">Baixa (Melhor Qualidade)</option><option value="medium" selected>Média (Equilibrado)</option><option value="high">Alta (Menor Tamanho)</option></select></div>` },
            'protect': { title: 'Proteger PDF', body: `<div class="mb-3"><label for="protectPassword" class="form-label">Defina uma senha:</label><input type="password" id="protectPassword" class="form-control" required></div><div class="mb-3"><label for="confirmPassword" class="form-label">Confirme a senha:</label><input type="password" id="confirmPassword" class="form-control" required></div>` },
            'unlock': { title: 'Remover Senha', body: `<div class="mb-3"><label for="unlockPassword" class="form-label">Digite a senha atual:</label><input type="password" id="unlockPassword" class="form-control" required></div>` },
            'pdf-to-word': { title: 'PDF para Word', body: `<p>O arquivo carregado (<strong>${uploadedFile?.name || 'PDF'}</strong>) será convertido. Clique em processar.</p>` },
            'pdf-to-excel': { title: 'PDF para Excel', body: `<p>O arquivo carregado (<strong>${uploadedFile?.name || 'PDF'}</strong>) será convertido. Clique em processar.</p>` },
            'pdf-to-image': { title: 'PDF para Imagens', body: `<p>O arquivo carregado (<strong>${uploadedFile?.name || 'PDF'}</strong>) será convertido. Clique em processar.</p>` },
        };
        
        const modalEl = document.getElementById('toolModal');
        const modalTitle = document.getElementById('toolModalTitle');
        const modalBody = document.getElementById('toolModalBody');
        const config = toolConfigs[tool] || { title: `Ferramenta: ${tool.replace(/-/g, ' ')}`, body: `<p>Esta ferramenta ainda não foi configurada.</p>` };
        modalTitle.textContent = config.title;
        modalBody.innerHTML = config.body;
        bootstrap.Modal.getOrCreateInstance(modalEl).show();

        if (tool === 'split') {
            toolState.split = { selections: [], rotations: [] };
            renderPagePreview(uploadedFile.file, uploadedFile);
            document.querySelectorAll('input[name="splitMode"]').forEach(radio => radio.addEventListener('change', handleSplitModeChange));
            document.getElementById('selectAllPages').addEventListener('change', (e) => App.toggleAllSelections(e.target.checked));
            document.getElementById('rotateAllBtn').addEventListener('click', () => App.rotateAllPreviews());
            handleSplitModeChange();
        }
    }

    // CORREÇÃO 2: Lógica ajustada para esconder apenas os controles de seleção, não a pré-visualização inteira.
    function handleSplitModeChange() {
        const selectedMode = document.querySelector('input[name="splitMode"]:checked').value;
        const pageControls = document.getElementById('splitPageControls');
        const previewContainer = document.getElementById('previewContainer');
        
        const showSelectionUI = selectedMode === 'individual' || selectedMode === 'merge';
        
        if (pageControls) {
            pageControls.style.display = showSelectionUI ? 'flex' : 'none';
        }
        
        if (previewContainer) {
            previewContainer.querySelectorAll('.card .form-check').forEach(el => {
                el.style.display = showSelectionUI ? 'flex' : 'none';
            });
        }
    }

    function renderPagePreview(file, uploadedFileInfo) {
        const previewContainer = document.getElementById('previewContainer');
        const numPages = uploadedFileInfo.numPages;
        previewContainer.innerHTML = `<div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Renderizando ${numPages} páginas...</div>`;

        const fileReader = new FileReader();
        fileReader.onload = (e) => {
            pdfjsLib.getDocument({ data: e.target.result }).promise.then(pdf => {
                previewContainer.innerHTML = '';
                toolState.split = { selections: Array(numPages).fill(false), rotations: Array(numPages).fill(0) };
                
                for (let i = 1; i <= numPages; i++) {
                    pdf.getPage(i).then(page => {
                        const canvas = document.createElement('canvas');
                        const scale = 0.3;
                        const viewport = page.getViewport({ scale });
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        page.render({ canvasContext: canvas.getContext('2d'), viewport: viewport });

                        const cardHTML = `<div class="col-xl-2 col-lg-3 col-md-4 col-sm-6"><div class="card h-100"><div class="card-body p-2 d-flex flex-column align-items-center"><div class="form-check d-flex align-items-center justify-content-center mb-2"><input class="form-check-input mt-0" type="checkbox" id="page-checkbox-${i-1}" onchange="App.togglePageSelection(${i-1})"><label class="form-check-label ms-2 small" for="page-checkbox-${i-1}">Página ${i}</label></div><div id="page-canvas-wrapper-${i-1}" class="my-1" style="transition: transform 0.3s ease;"></div><button class="btn btn-outline-secondary btn-sm" onclick="App.rotatePagePreview(${i-1})"><i class="fas fa-sync-alt"></i> Girar</button></div></div></div>`;
                        previewContainer.insertAdjacentHTML('beforeend', cardHTML);
                        document.getElementById(`page-canvas-wrapper-${i-1}`).appendChild(canvas);
                    });
                }
                // Chama a função após renderizar para garantir que o estado inicial da UI esteja correto.
                setTimeout(handleSplitModeChange, 100); 
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
                    } else { throw new Error(result.message || 'Ocorreu um erro no servidor.'); }
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
                const splitMode = document.querySelector('input[name="splitMode"]:checked').value;
                if ((splitMode === 'individual' || splitMode === 'merge') && toolState.split.selections.every(s => !s)) {
                    throw new Error('Nenhuma página foi selecionada.');
                }
                formData.append('split_mode', splitMode);
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
            case 'unlock':
                const unlockPassword = document.getElementById('unlockPassword').value;
                if (!unlockPassword) throw new Error('Por favor, digite a senha atual do PDF.');
                formData.append('password', unlockPassword);
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
        if (result.download_zip) {
            content += `<div class="text-center mb-3"><a href="${result.download_zip}" class="btn btn-success btn-lg" download><i class="fas fa-file-archive me-2"></i>Baixar Arquivos (.zip)</a></div>`;
        }
        modalBody.innerHTML = content;
        modal.show();
    }
});

window.App = {
    rotatePagePreview: function(pageIndex) {
        toolState.split.rotations[pageIndex] = (toolState.split.rotations[pageIndex] + 90) % 360;
        const wrapper = document.getElementById(`page-canvas-wrapper-${pageIndex}`);
        if (wrapper) wrapper.style.transform = `rotate(${toolState.split.rotations[pageIndex]}deg)`;
    },
    togglePageSelection: function(pageIndex) {
        toolState.split.selections[pageIndex] = !toolState.split.selections[pageIndex];
        document.getElementById('selectAllPages').checked = toolState.split.selections.every(s => s);
    },
    toggleAllSelections: function(isChecked) {
        toolState.split.selections.fill(isChecked);
        for (let i = 0; i < toolState.split.selections.length; i++) {
            const checkbox = document.getElementById(`page-checkbox-${i}`);
            if (checkbox) checkbox.checked = isChecked;
        }
    },
    rotateAllPreviews: function() {
        for (let i = 0; i < toolState.split.rotations.length; i++) {
            this.rotatePagePreview(i);
        }
    }
};
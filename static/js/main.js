// =========================================================================
// static/js/main.js (VERSÃO FINAL COM CORREÇÃO DE LÓGICA ASSÍNCRONA)
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
        image: { rotations: [] },
        convertImage: { rotation: 0 },
        merge: { files: [], rotations: {} }
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
        const toolConfigs = {
            'merge': { title: 'Unir PDFs', body: `<div class="mb-3"><label for="mergeFilesInput" class="form-label">Selecione dois ou mais arquivos PDF:</label><input type="file" id="mergeFilesInput" class="form-control" multiple accept=".pdf"></div><div id="previewContainer" class="row g-3"><p class="text-muted text-center">Nenhum arquivo selecionado.</p></div>` },
            'split': { title: 'Dividir PDF', body: `<div class="row border-bottom pb-3 mb-3"><div class="col-md-7"><h6>Modo de Divisão</h6><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitIndividual" value="individual" checked><label class="form-check-label" for="splitIndividual">Extrair páginas selecionadas (.zip)</label></div><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitMerge" value="merge"><label class="form-check-label" for="splitMerge">Unir páginas selecionadas</label></div><div class="form-check"><input class="form-check-input" type="radio" name="splitMode" id="splitPairs" value="pairs"><label class="form-check-label" for="splitPairs">Dividir em pares</label></div></div><div class="col-md-5 d-flex align-items-center justify-content-end" id="splitPageControls"><div class="form-check me-3"><input class="form-check-input" type="checkbox" id="selectAllPages"><label class="form-check-label" for="selectAllPages">Selecionar Todas</label></div><button class="btn btn-secondary" id="rotateAllBtn"><i class="fas fa-sync-alt me-2"></i>Girar Todas</button></div></div><div id="previewContainer" class="row g-3 text-center"><div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Carregando...</div></div>` },
            'compress': { title: 'Comprimir PDF', body: `<div class="mb-3"><label for="compressionLevel" class="form-label">Nível de Compressão:</label><select id="compressionLevel" class="form-select"><option value="low">Baixa (Melhor Qualidade)</option><option value="medium" selected>Média (Equilibrado)</option><option value="high">Alta (Menor Tamanho)</option></select></div>` },
            'protect': { title: 'Proteger PDF', body: `<div class="mb-3"><label for="protectPassword" class="form-label">Defina uma senha:</label><input type="password" id="protectPassword" class="form-control" required></div><div class="mb-3"><label for="confirmPassword" class="form-label">Confirme a senha:</label><input type="password" id="confirmPassword" class="form-control" required></div>` },
            'unlock': { title: 'Remover Senha', body: `<div class="mb-3"><label for="unlockPassword" class="form-label">Digite a senha atual:</label><input type="password" id="unlockPassword" class="form-control" required></div>` },
            'pdf-to-word': { title: 'PDF para Word', body: `<p>O arquivo carregado (<strong>${uploadedFile?.name || 'PDF'}</strong>) será convertido. Clique em processar.</p>` },
            'pdf-to-excel': { title: 'PDF para Excel', body: `<p>O arquivo carregado (<strong>${uploadedFile?.name || 'PDF'}</strong>) será convertido. Clique em processar.</p>` },
            'pdf-to-image': { title: 'Converter PDF para Imagens', body: `<div class="d-flex justify-content-between align-items-center mb-3"><div><label class="form-label mb-0 me-2" for="imageFormat">Formato:</label><select class="form-select-sm" id="imageFormat"><option value="jpg">JPG</option><option value="png" selected>PNG</option></select></div><button class="btn btn-secondary" id="rotateAllBtn"><i class="fas fa-sync-alt me-2"></i>Girar Todas</button></div><div id="previewContainer" class="row g-3 text-center"><div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Carregando...</div></div>` },
            'image-to-pdf': { title: 'Imagens para PDF', body: `<div class="mb-3"><label for="imageFilesInput" class="form-label">Selecione uma ou mais imagens:</label><input type="file" id="imageFilesInput" class="form-control" multiple accept="image/*"></div><div id="imageListPreview" class="mt-3"><p class="text-muted">Nenhuma imagem selecionada.</p></div>` },
            'convert-image': { title: 'Converter Formato de Imagem', body: `<div class="row"><div class="col-md-7"><div class="mb-3"><label for="convertImageInput" class="form-label">Selecione uma imagem:</label><input type="file" id="convertImageInput" class="form-control" accept="image/*"></div><div id="convertImageOptions" class="d-none"><div class="mb-3"><label class="form-label">Converter de <strong id="originalFormat"></strong> para:</label><select id="targetFormatSelect" class="form-select"></select></div><button class="btn btn-secondary" id="rotateImageBtn"><i class="fas fa-sync-alt"></i> Girar Imagem</button></div></div><div class="col-md-5 d-flex align-items-center justify-content-center"><div id="imagePreviewContainer" class="text-center"><p class="text-muted">Pré-visualização</p></div></div></div>` }
        };
        const modalEl = document.getElementById('toolModal');
        const modalTitle = document.getElementById('toolModalTitle');
        const modalBody = document.getElementById('toolModalBody');
        const config = toolConfigs[tool] || { title: `Ferramenta: ${tool.replace(/-/g, ' ')}`, body: `<p>Esta ferramenta ainda não foi configurada.</p>` };
        modalTitle.textContent = config.title;
        modalBody.innerHTML = config.body;
        bootstrap.Modal.getOrCreateInstance(modalEl).show();

        switch (tool) {
            case 'merge': toolState.merge = { files: [], rotations: {} }; document.getElementById('mergeFilesInput').addEventListener('change', window.App.renderMergePreview); break;
            case 'split':
                toolState.split = { selections: [], rotations: [] };
                renderPagePreview(uploadedFile.file, uploadedFile, 'split');
                document.querySelectorAll('input[name="splitMode"]').forEach(radio => radio.addEventListener('change', handleSplitModeChange));
                document.getElementById('selectAllPages').addEventListener('change', (e) => window.App.toggleAllSelections(e.target.checked));
                document.getElementById('rotateAllBtn').addEventListener('click', () => window.App.rotateAllPreviews('split'));
                handleSplitModeChange();
                break;
            case 'pdf-to-image': toolState.image = { rotations: [] }; renderPagePreview(uploadedFile.file, uploadedFile, 'image'); document.getElementById('rotateAllBtn').addEventListener('click', () => window.App.rotateAllPreviews('image')); break;
            case 'image-to-pdf': document.getElementById('imageFilesInput').addEventListener('change', handleImageToPdfPreview); break;
            case 'convert-image': toolState.convertImage = { rotation: 0 }; document.getElementById('convertImageInput').addEventListener('change', renderImageConverterPreview); document.getElementById('rotateImageBtn').addEventListener('click', window.App.rotateConvertImage); break;
        }
    }

    function handleSplitModeChange() {
        const selectedMode = document.querySelector('input[name="splitMode"]:checked').value;
        const pageControls = document.getElementById('splitPageControls');
        const previewContainer = document.getElementById('previewContainer');
        const showSelectionUI = selectedMode === 'individual' || selectedMode === 'merge';
        if (pageControls) pageControls.style.display = showSelectionUI ? 'flex' : 'none';
        if (previewContainer) {
            previewContainer.querySelectorAll('.card .form-check').forEach(el => {
                el.style.display = showSelectionUI ? 'flex' : 'none';
            });
        }
    }

    function renderPagePreview(file, uploadedFileInfo, mode) {
        const previewContainer = document.getElementById('previewContainer');
        const numPages = uploadedFileInfo.numPages;
        previewContainer.innerHTML = `<div class="col-12"><i class="fas fa-spinner fa-spin me-2"></i>Renderizando ${numPages} páginas...</div>`;
        const fileReader = new FileReader();
        fileReader.onload = (e) => {
            pdfjsLib.getDocument({ data: e.target.result }).promise.then(pdf => {
                previewContainer.innerHTML = '';
                if (mode === 'split') toolState.split = { selections: Array(numPages).fill(false), rotations: Array(numPages).fill(0) };
                if (mode === 'image') toolState.image = { rotations: Array(numPages).fill(0) };
                for (let i = 1; i <= numPages; i++) {
                    pdf.getPage(i).then(page => {
                        const canvas = document.createElement('canvas');
                        const scale = 0.3;
                        const viewport = page.getViewport({ scale });
                        canvas.height = viewport.height; canvas.width = viewport.width;
                        page.render({ canvasContext: canvas.getContext('2d'), viewport: viewport });
                        let optionsHTML = `<p class="mb-1 mt-2 small">Página ${i}</p>`;
                        if (mode === 'split') {
                            optionsHTML = `<div class="form-check d-flex align-items-center justify-content-center mb-2"><input class="form-check-input mt-0" type="checkbox" id="page-checkbox-${i-1}" onchange="window.App.togglePageSelection(${i-1})"><label class="form-check-label ms-2 small" for="page-checkbox-${i-1}">Página ${i}</label></div>`;
                        }
                        const cardHTML = `<div class="col-xl-2 col-lg-3 col-md-4 col-sm-6"><div class="card h-100"><div class="card-body p-2 d-flex flex-column align-items-center">${optionsHTML}<div id="page-canvas-wrapper-${i-1}" class="my-1" style="transition: transform 0.3s ease;"></div><button class="btn btn-outline-secondary btn-sm" onclick="window.App.rotatePagePreview(${i-1}, '${mode}')"><i class="fas fa-sync-alt"></i> Girar</button></div></div></div>`;
                        previewContainer.insertAdjacentHTML('beforeend', cardHTML);
                        document.getElementById(`page-canvas-wrapper-${i-1}`).appendChild(canvas);
                    });
                }
                if (mode === 'split') setTimeout(handleSplitModeChange, 100);
            });
        };
        fileReader.readAsArrayBuffer(file);
    }
    
    function handleImageToPdfPreview(event) {
        const files = event.target.files;
        const previewContainer = document.getElementById('imageListPreview');
        previewContainer.innerHTML = '';
        if (files.length > 0) {
            let fileListHTML = '<h6>Imagens Selecionadas:</h6><ul class="list-group">';
            Array.from(files).forEach(file => { fileListHTML += `<li class="list-group-item d-flex align-items-center"><i class="fas fa-file-image me-2 text-info"></i>${file.name}</li>`; });
            fileListHTML += '</ul>';
            previewContainer.innerHTML = fileListHTML;
        } else { previewContainer.innerHTML = '<p class="text-muted">Nenhuma imagem selecionada.</p>'; }
    }
    
    function renderImageConverterPreview(event) {
        const file = event.target.files[0];
        if (!file) return;
        const previewContainer = document.getElementById('imagePreviewContainer');
        const optionsContainer = document.getElementById('convertImageOptions');
        const reader = new FileReader();
        reader.onload = (e) => { previewContainer.innerHTML = `<img id="imagePreview" src="${e.target.result}" class="img-fluid" style="max-height: 250px; transition: transform 0.3s ease;">`; };
        reader.readAsDataURL(file);
        const originalFormat = file.type.split('/')[1].toUpperCase().replace('JPEG', 'JPG');
        document.getElementById('originalFormat').textContent = originalFormat;
        const availableFormats = ['PNG', 'JPG', 'WEBP', 'BMP', 'TIFF'];
        const targetSelect = document.getElementById('targetFormatSelect');
        targetSelect.innerHTML = '';
        availableFormats.forEach(format => {
            if (format !== originalFormat) {
                const option = document.createElement('option');
                option.value = format.toLowerCase();
                option.textContent = format;
                targetSelect.appendChild(option);
            }
        });
        optionsContainer.classList.remove('d-none');
    }

    const processButton = document.getElementById('processTool');
    if (processButton) {
        processButton.addEventListener('click', function() {
            const button = this;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processando...';
            button.disabled = true;

            // --- LÓGICA DE EXECUÇÃO CORRIGIDA ---
            prepareAndSendData()
                .then(result => {
                    if (result.success) {
                        bootstrap.Modal.getInstance(document.getElementById('toolModal')).hide();
                        showResults(result);
                    } else {
                        // Se o backend retornou `success: false`, mostra a mensagem dele
                        throw new Error(result.message || 'Ocorreu um erro no servidor.');
                    }
                })
                .catch(error => {
                    // Trata erros de validação do front-end ou de comunicação com o servidor
                    alert(`Erro: ${error.message}`);
                })
                .finally(() => {
                    button.innerHTML = 'Processar';
                    button.disabled = false;
                });
        });
    }

    // Nova função para encapsular a preparação dos dados
    function prepareAndSendData() {
        return new Promise((resolve, reject) => {
            try {
                const formData = new FormData();
                switch (selectedTool) {
                    case 'merge':
                        const mergeInput = document.getElementById('mergeFilesInput');
                        if (mergeInput.files.length < 2) throw new Error('Selecione pelo menos 2 arquivos para unir.');
                        Array.from(mergeInput.files).forEach(file => formData.append('files', file));
                        formData.append('rotations', JSON.stringify(toolState.merge.rotations));
                        break;
                    case 'convert-image':
                        const imageInput = document.getElementById('convertImageInput');
                        if (imageInput.files.length === 0) throw new Error('Nenhum arquivo de imagem selecionado.');
                        formData.append('file', imageInput.files[0]);
                        formData.append('target_format', document.getElementById('targetFormatSelect').value);
                        formData.append('rotation', toolState.convertImage.rotation);
                        break;
                    case 'image-to-pdf':
                        const imagesInput = document.getElementById('imageFilesInput');
                        if (imagesInput.files.length === 0) throw new Error('Nenhum arquivo de imagem selecionado.');
                        Array.from(imagesInput.files).forEach(file => { formData.append('files', file); });
                        break;
                    case 'split':
                        formData.append('file', uploadedFile.file);
                        const splitMode = document.querySelector('input[name="splitMode"]:checked').value;
                        formData.append('split_mode', splitMode);
                        formData.append('selections', JSON.stringify(toolState.split.selections));
                        formData.append('rotations', JSON.stringify(toolState.split.rotations));
                        break;
                    case 'compress':
                        formData.append('file', uploadedFile.file);
                        formData.append('compression_level', document.getElementById('compressionLevel').value);
                        break;
                    case 'protect':
                        formData.append('file', uploadedFile.file);
                        const password = document.getElementById('protectPassword').value;
                        if (!password) throw new Error('A senha não pode estar vazia.');
                        if (password !== document.getElementById('confirmPassword').value) throw new Error('As senhas não coincidem.');
                        formData.append('password', password);
                        break;
                    case 'unlock':
                        formData.append('file', uploadedFile.file);
                        formData.append('password', document.getElementById('unlockPassword').value);
                        break;
                    case 'pdf-to-image':
                        formData.append('file', uploadedFile.file);
                        formData.append('image_format', document.getElementById('imageFormat').value);
                        formData.append('rotations', JSON.stringify(toolState.image.rotations));
                        break;
                    default:
                        formData.append('file', uploadedFile.file);
                        break;
                }
                
                // Envia os dados e resolve a Promise com o resultado
                fetch(`/api/${selectedTool}/`, { method: 'POST', headers: { 'X-CSRFToken': csrftoken }, body: formData })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().catch(() => ({ success: false, message: `Erro no servidor: ${response.status} ${response.statusText}` })).then(err => { throw err; });
                        }
                        return response.json();
                    })
                    .then(resolve)
                    .catch(reject);

            } catch (error) {
                // Rejeita a Promise se houver um erro de validação do lado do cliente
                reject(error);
            }
        });
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

    window.App = {
        rotatePagePreview: function(pageIndex, mode) {
            const state = toolState[mode];
            state.rotations[pageIndex] = (state.rotations[pageIndex] + 90) % 360;
            const wrapper = document.getElementById(`page-canvas-wrapper-${pageIndex}`);
            if (wrapper) wrapper.style.transform = `rotate(${state.rotations[pageIndex]}deg)`;
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
        rotateAllPreviews: function(mode) {
            const state = toolState[mode];
            for (let i = 0; i < state.rotations.length; i++) { this.rotatePagePreview(i, mode); }
        },
        rotateConvertImage: function() {
            toolState.convertImage.rotation = (toolState.convertImage.rotation + 90) % 360;
            const img = document.getElementById('imagePreview');
            if (img) img.style.transform = `rotate(${toolState.convertImage.rotation}deg)`;
        }
    };
});
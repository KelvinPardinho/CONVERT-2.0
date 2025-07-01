// =========================================================================
// static/js/main.js - Versão Profissional e Otimizada
// =========================================================================

/**
 * Função principal que é executada quando o DOM está totalmente carregado.
 * Inicializa todas as funcionalidades globais do site.
 */
document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializa o toggle de tema escuro/claro
    initializeThemeToggle();

    // Adiciona funcionalidade de smooth scrolling para links de âncora
    initializeSmoothScrolling();

    // Inicializa tooltips do Bootstrap, se houver
    if (window.bootstrap && typeof window.bootstrap.Tooltip === 'function') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});


/**
 * Inicializa o botão de alternância de tema (Dark/Light Mode).
 * - Verifica o tema salvo no localStorage.
 * - Ouve a preferência do sistema operacional do usuário.
 * - Atualiza o ícone e a classe no body.
 */
function initializeThemeToggle() {
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeIcon = document.getElementById('theme-icon');
    
    if (!themeToggleButton || !themeIcon) return;

    // Função para aplicar o tema e atualizar o ícone
    const applyTheme = (theme) => {
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        } else {
            document.body.classList.remove('dark-mode');
            themeIcon.classList.remove('fa-sun');
            themeIcon.classList.add('fa-moon');
        }
    };

    // Verifica o tema salvo ou a preferência do sistema
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
    
    applyTheme(initialTheme);

    // Adiciona o listener de clique para alternar o tema
    themeToggleButton.addEventListener('click', function() {
        const isDarkMode = document.body.classList.toggle('dark-mode');
        const newTheme = isDarkMode ? 'dark' : 'light';
        localStorage.setItem('theme', newTheme);
        applyTheme(newTheme);
    });
}


/**
 * Adiciona rolagem suave para links que apontam para âncoras na mesma página.
 */
function initializeSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}


/**
 * Exibe uma mensagem de alerta customizada no topo da página.
 * @param {string} message - A mensagem a ser exibida.
 * @param {string} type - O tipo de alerta (e.g., 'success', 'danger', 'info').
 * @param {number} duration - Duração em milissegundos para o alerta desaparecer (0 para não desaparecer).
 */
function showAlert(message, type = 'info', duration = 5000) {
    const alertWrapper = document.createElement('div');
    alertWrapper.style.position = 'fixed';
    alertWrapper.style.top = '80px';
    alertWrapper.style.right = '20px';
    alertWrapper.style.zIndex = '1050'; // Acima da maioria dos elementos

    const alertEl = document.createElement('div');
    alertEl.className = `alert alert-${type} alert-dismissible fade show shadow-lg`;
    alertEl.role = 'alert';
    alertEl.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertWrapper.appendChild(alertEl);
    document.body.appendChild(alertWrapper);

    if (duration > 0) {
        setTimeout(() => {
            if (alertWrapper.parentNode) {
                // Inicia o fade-out antes de remover
                alertEl.classList.remove('show');
                alertEl.addEventListener('transitionend', () => alertWrapper.remove());
            }
        }, duration);
    }
}

/**
 * Formata o tamanho do arquivo de bytes para uma string legível (KB, MB).
 * @param {number} bytes - O tamanho do arquivo em bytes.
 * @returns {string} - A string formatada.
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Expondo funções úteis globalmente sob um namespace para evitar poluição
window.AppUtils = {
    showAlert,
    formatFileSize
};
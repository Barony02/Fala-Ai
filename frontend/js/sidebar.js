const container = document.getElementById("sidebar-container");
const THEME_KEY = "fala_ai_theme";

function aplicarTemaSalvo() {
    const tema = localStorage.getItem(THEME_KEY) || "light";
    document.documentElement.setAttribute("data-theme", tema);
}

aplicarTemaSalvo();

function garantirToastContainer() {
    let container = document.getElementById("toast-global-container");
    if (!container) {
        container = document.createElement("div");
        container.id = "toast-global-container";
        document.body.appendChild(container);
    }
    return container;
}

window.falaAiToast = function (mensagem, tipo = "info") {
    const container = garantirToastContainer();
    const toast = document.createElement("div");
    toast.className = `toast-global ${tipo}`;
    toast.textContent = mensagem;
    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 250);
    }, 3500);
};

function carregarSidebar() {
    if (!container) return;

    const sidebarCache = sessionStorage.getItem('sidebar_html');
    
    if (sidebarCache && sidebarCache.includes("btn-theme-toggle") && sidebarCache.includes("relatorios.html")) {
        montarSidebar(sidebarCache);
    } else {
        fetch('/components/sidebar.html')
            .then(res => res.text())
            .then(html => {
                sessionStorage.setItem('sidebar_html', html);
                montarSidebar(html);
            });
    }
}

function montarSidebar(html) {
    container.innerHTML = html;
    configurarVisibilidadePorPerfil();
    destacarMenuAtivo();
    configurarTema();
    configurarBotaoSair();
}

function configurarVisibilidadePorPerfil() {
    const perfil = sessionStorage.getItem('perfil'); 

    if (perfil === 'Gestor' || perfil === 'Administrador') {
        document.querySelectorAll('.admin-gestor-view').forEach(el => el.style.display = 'flex');
    } 
}

function destacarMenuAtivo() {
    const pathAtual = window.location.pathname;
    const links = document.querySelectorAll("#sidebar-container .menu-btn");
    
    links.forEach(link => {
        if (pathAtual === link.getAttribute("href")) {
            link.classList.add("active");
        }
    });
}

function configurarBotaoSair() {
    const btnSair = document.getElementById("btn-sair");
    if (btnSair) {
        btnSair.addEventListener("click", () => {
            sessionStorage.removeItem('sidebar_html');
            sessionStorage.removeItem('perfil'); 
            window.location.href = "/index.html"; 
        });
    }
}

function configurarTema() {
    const btnTema = document.getElementById("btn-theme-toggle");
    if (!btnTema) return;

    function renderizarBotao() {
        const temaAtual = document.documentElement.getAttribute("data-theme") || "light";
        const escuro = temaAtual === "dark";
        btnTema.innerHTML = escuro
            ? '<i class="fas fa-sun"></i> <span>Modo claro</span>'
            : '<i class="fas fa-moon"></i> <span>Modo escuro</span>';
    }

    btnTema.addEventListener("click", () => {
        const temaAtual = document.documentElement.getAttribute("data-theme") || "light";
        const novoTema = temaAtual === "dark" ? "light" : "dark";
        localStorage.setItem(THEME_KEY, novoTema);
        document.documentElement.setAttribute("data-theme", novoTema);
        renderizarBotao();
    });

    renderizarBotao();
}

// Executa imediatamente
carregarSidebar();

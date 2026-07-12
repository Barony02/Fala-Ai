const container = document.getElementById("sidebar-container");

function carregarSidebar() {
    if (!container) return;

    const sidebarCache = sessionStorage.getItem('sidebar_html');
    
    if (sidebarCache) {
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

// Executa imediatamente
carregarSidebar();
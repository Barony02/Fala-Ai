document.addEventListener("DOMContentLoaded", () => {
    inicializarPerfil();
    configurarFormularioPerfil();
    configurarFormularioSenha();
});

// Função auxiliar para gerar e remover as notificações dinamicamente
function mostrarToast(mensagem, tipo = "sucesso") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast ${tipo}`;
    toast.textContent = mensagem;

    container.appendChild(toast);

    // Remove o toast automaticamente após 4 segundos
    setTimeout(() => {
        toast.classList.add("fade-out");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function obterHeadersAutenticados() {
    const token = localStorage.getItem("token");
    return {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
    };
}

async function inicializarPerfil() {
    try {
        const headers = obterHeadersAutenticados();
        const response = await fetch("http://localhost:8000/api/usuarios/perfil/me", {
            method: "GET",
            headers: headers
        });

        if (!response.ok) {
            throw new Error("Erro ao carregar os dados do perfil.");
        }

        const usuario = await response.json();

        document.getElementById("summary-name").textContent = usuario.nome;
        document.getElementById("summary-setor").textContent = `Setor: ${usuario.setor}`;
        
        const badgePerfil = document.getElementById("summary-perfil");
        badgePerfil.textContent = usuario.perfil;
        badgePerfil.className = `badge ${usuario.perfil.toLowerCase()}`;

        const iniciais = usuario.nome.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();
        document.getElementById("user-avatar").textContent = iniciais;

        document.getElementById("input-nome").value = usuario.nome;
        document.getElementById("input-email").value = usuario.email;
        document.getElementById("input-matricula").value = usuario.matricula;

    } catch (error) {
        mostrarToast("Sua sessão expirou ou ocorreu um erro de conexão.", "erro");
        setTimeout(() => {
            window.location.href = "index.html";
        }, 2000);
    }
}

function configurarFormularioPerfil() {
    const formPerfil = document.getElementById("form-perfil");
    
    formPerfil.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const nomeAlterado = document.getElementById("input-nome").value;

        if (!nomeAlterado.trim()) {
            mostrarToast("O campo Nome não pode estar vazio.", "erro");
            return;
        }

        try {
            const response = await fetch("http://localhost:8000/api/usuarios/me/perfil", {
                method: "PUT",
                headers: obterHeadersAutenticados(),
                body: JSON.stringify({ nome: nomeAlterado })
            });

            const data = await response.json();

            if (response.ok) {
                mostrarToast(data.mensagem || "Informações pessoais atualizadas!", "sucesso");
                
                document.getElementById("summary-name").textContent = nomeAlterado;
                const iniciais = nomeAlterado.split(" ").map(n => n[0]).slice(0, 2).join("").toUpperCase();
                document.getElementById("user-avatar").textContent = iniciais;
            } else {
                mostrarToast(data.detail || "Erro ao atualizar informações.", "erro");
            }
        } catch (error) {
            mostrarToast("Erro ao conectar com o servidor.", "erro");
        }
    });
}

function configurarFormularioSenha() {
    const formSenha = document.getElementById("form-senha");

    formSenha.addEventListener("submit", async (e) => {
        e.preventDefault();

        const senhaAtual = document.getElementById("senha-atual").value;
        const novaSenha = document.getElementById("nova-senha").value;
        const confirmarSenha = document.getElementById("confirmar-senha").value;

        if (novaSenha.length < 6) {
            mostrarToast("A nova senha deve conter pelo menos 6 caracteres.", "erro");
            return;
        }

        if (novaSenha !== confirmarSenha) {
            mostrarToast("A nova senha e a confirmação não coincidem.", "erro");
            return;
        }

        if (senhaAtual === novaSenha) {
            mostrarToast("A nova senha não pode ser igual à senha atual.", "erro");
            return;
        }

        try {
            const response = await fetch("http://localhost:8000/api/usuarios/me/senha", {
                method: "PUT",
                headers: obterHeadersAutenticados(),
                body: JSON.stringify({
                    senha_atual: senhaAtual,
                    nova_senha: novaSenha
                })
            });

            const data = await response.json();

            if (response.ok) {
                mostrarToast(data.mensagem || "Senha atualizada com sucesso!", "sucesso");
                formSenha.reset();
            } else {
                mostrarToast(data.detail || "Erro ao alterar a senha.", "erro");
            }
        } catch (error) {
            mostrarToast("Erro ao tentar atualizar a senha.", "erro");
        }
    });
}
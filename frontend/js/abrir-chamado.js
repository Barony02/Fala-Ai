// abrir-chamado.js
const API_URL = window.location.hostname === 'localhost' 
    ? "http://localhost:8000/api"
    : `${window.location.protocol}//${window.location.hostname}:8000/api`;

const form = document.getElementById("chamadoForm");
const mensagem = document.getElementById("mensagem");
const selectResponsavel = document.getElementById("setorResponsavel");
const selectUsuarioResponsavel = document.getElementById("usuarioResponsavel");

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/index.html";
        return;
    }
    
    carregarSetores();
});

async function carregarSetores() {
    try {
        const token = localStorage.getItem("token");
        
        const response = await fetch(`${API_URL}/setores`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error("Erro ao carregar setores");
        }

        const setores = await response.json();
        
        selectResponsavel.innerHTML = '<option value="">Selecione...</option>';

        if (!setores || setores.length === 0) {
            selectResponsavel.innerHTML += '<option disabled>Nenhum setor disponível</option>';
            return;
        }

        setores.forEach(setor => {
            const option = document.createElement("option");
            option.value = setor.id;
            option.textContent = setor.nome;
            selectResponsavel.appendChild(option);
        });

    } catch (error) {
        console.error("Erro ao carregar setores:", error);
        mostrarMensagem("Erro ao carregar setores", "erro");
    }
}

selectResponsavel.addEventListener("change", async () => {
    const setorId = selectResponsavel.value;
    
    if (!setorId) {
        selectUsuarioResponsavel.innerHTML = '<option value="">Selecione um setor primeiro...</option>';
        selectUsuarioResponsavel.disabled = true;
        return;
    }

    try {
        const token = localStorage.getItem("token");
        selectUsuarioResponsavel.innerHTML = '<option value="">Carregando usuários...</option>';
        selectUsuarioResponsavel.disabled = true;

        const response = await fetch(`${API_URL}/setores/${setorId}/usuarios`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error("Erro ao carregar usuários do setor");
        }

        const usuarios = await response.json();
        
        selectUsuarioResponsavel.innerHTML = '<option value="">Enviar para todos (Nenhum específico)</option>';
        selectUsuarioResponsavel.disabled = false;

        usuarios.forEach(usuario => {
            const option = document.createElement("option");
            option.value = usuario.id;
            option.textContent = usuario.nome;
            selectUsuarioResponsavel.appendChild(option);
        });

    } catch (error) {
        console.error("Erro ao carregar usuários:", error);
        selectUsuarioResponsavel.innerHTML = '<option value="">Enviar para todos (Nenhum específico)</option>';
        selectUsuarioResponsavel.disabled = false;
    }
});

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/index.html";
        return;
    }

    const titulo = document.getElementById("titulo").value.trim();
    const descricao = document.getElementById("descricao").value.trim();
    const setorResponsavel = selectResponsavel.value;
    const usuarioResponsavel = selectUsuarioResponsavel.value;
    const prioridade = document.getElementById("prioridade").value;

    if (!titulo || !descricao || !setorResponsavel || !prioridade) {
        mostrarMensagem("Preencha todos os campos obrigatórios", "erro");
        return;
    }

    try {
        mostrarMensagem("Enviando...", "carregando");

        const response = await fetch(`${API_URL}/realizarChamado`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                titulo,
                descricao,
                setor_solicitante_id: 0, 
                setor_responsavel_id: parseInt(setorResponsavel),
                prioridade,
                usuario_responsavel_id: usuarioResponsavel ? parseInt(usuarioResponsavel) : null
            })
        });

        const data = await response.json();

        if (response.ok) {
            mostrarMensagem("Chamado aberto com sucesso!", "sucesso");
            form.reset();
            selectUsuarioResponsavel.innerHTML = '<option value="">Selecione um setor primeiro...</option>';
            selectUsuarioResponsavel.disabled = true;
            setTimeout(() => {
                window.location.href = "/app/meus-chamados.html";
            }, 1500);
        } else {
            mostrarMensagem(data.detail || "Erro ao abrir chamado", "erro");
        }
    } catch (error) {
        mostrarMensagem("Erro ao conectar com o servidor", "erro");
    }
});

function mostrarMensagem(texto, tipo) {
    mensagem.textContent = texto;
    mensagem.className = `mensagem ${tipo}`;
}
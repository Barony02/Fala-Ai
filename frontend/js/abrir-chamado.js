// Detectar a URL da API dinamicamente
const API_URL = window.location.hostname === 'localhost' 
    ? "http://localhost:8000/api"
    : `${window.location.protocol}//${window.location.hostname}:8000/api`;

const form = document.getElementById("chamadoForm");
const mensagem = document.getElementById("mensagem");
// Verificar autenticação e carregar setores ao iniciar
document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/index.html";
        return;
    }
    
    carregarSetores();
});

// Carregar setores
async function carregarSetores() {
    try {
        const token = localStorage.getItem("token");
        console.log("Token:", token ? "Existe" : "Não existe");
        
        const response = await fetch(`${API_URL}/setores`, {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        console.log("Status da resposta:", response.status);
        console.log("OK?", response.ok);

        if (!response.ok) {
            console.error("Erro na resposta:", response.statusText);
            throw new Error("Erro ao carregar setores");
        }

        const setores = await response.json();
        console.log("Setores recebidos:", setores);
        
        const selectSolicitante = document.getElementById("setorSolicitante");
        const selectResponsavel = document.getElementById("setorResponsavel");

        selectSolicitante.innerHTML = '<option value="">Selecione...</option>';
        selectResponsavel.innerHTML = '<option value="">Selecione...</option>';

        if (!setores || setores.length === 0) {
            console.warn("Nenhum setor retornado");
            selectSolicitante.innerHTML += '<option disabled>Nenhum setor disponível</option>';
            selectResponsavel.innerHTML += '<option disabled>Nenhum setor disponível</option>';
            return;
        }

        setores.forEach(setor => {
            console.log("Adicionando setor:", setor);
            
            const option1 = document.createElement("option");
            option1.value = setor.id;
            option1.textContent = setor.nome;
            selectSolicitante.appendChild(option1);

            const option2 = document.createElement("option");
            option2.value = setor.id;
            option2.textContent = setor.nome;
            selectResponsavel.appendChild(option2);
        });

        console.log("Setores carregados com sucesso");
    } catch (error) {
        console.error("Erro ao carregar setores:", error);
        mostrarMensagem("Erro ao carregar setores", "erro");
    }
}

// Enviar formulário
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/index.html";
        return;
    }

    const titulo = document.getElementById("titulo").value.trim();
    const descricao = document.getElementById("descricao").value.trim();
    const setorSolicitante = document.getElementById("setorSolicitante").value;
    const setorResponsavel = document.getElementById("setorResponsavel").value;
    const prioridade = document.getElementById("prioridade").value;

    // Validação
    if (!titulo || !descricao || !setorSolicitante || !setorResponsavel || !prioridade) {
        mostrarMensagem("Preencha todos os campos", "erro");
        return;
    }

    if (setorSolicitante === setorResponsavel) {
        mostrarMensagem("Os setores devem ser diferentes", "erro");
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
                setor_solicitante_id: parseInt(setorSolicitante),
                setor_responsavel_id: parseInt(setorResponsavel),
                prioridade
            })
        });

        const data = await response.json();

        if (response.ok) {
            mostrarMensagem("Chamado aberto com sucesso!", "sucesso");
            form.reset();
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

document.addEventListener("DOMContentLoaded", () => {
    const perfilLogado = sessionStorage.getItem("perfil");
    const token = localStorage.getItem("token");

    if (perfilLogado !== "Gestor" && perfilLogado !== "Administrador") {
        window.location.href = "/app/dashboard.html";
        return;
    }

    document.getElementById("info-perfil").textContent = `Perfil atual: ${perfilLogado}`;
    
    const btnNovoSetor = document.getElementById("btn-abrir-cadastro");
    if (perfilLogado === "Gestor") {
        btnNovoSetor.disabled = true;
        btnNovoSetor.title = "Apenas administradores podem cadastrar setores";
    }

    const modal = document.getElementById("modalForm");
    const form = document.getElementById("setorForm");
    const tabelaSetores = document.getElementById("tabela-setores");
    const painelChamados = document.getElementById("painel-chamados");
    const tabelaChamados = document.getElementById("tabela-chamados-setor");
    const tituloChamados = document.getElementById("titulo-chamados-setor");

    carregarPainelSetores();

    btnNovoSetor.addEventListener("click", () => abrirModal());
    document.getElementById("btn-fechar-modal").addEventListener("click", () => fecharModal());

    function abrirModal(dados = null) {
        if (dados) {
            document.getElementById("form-title").textContent = "Editar Setor";
            document.getElementById("setorId").value = dados.id;
            document.getElementById("nome").value = dados.nome;
            document.getElementById("sigla").value = dados.sigla;
        } else {
            document.getElementById("form-title").textContent = "Cadastrar Setor";
            form.reset();
            document.getElementById("setorId").value = "";
        }
        modal.style.display = "flex";
    }

    function fecharModal() {
        modal.style.display = "none";
        form.reset();
    }

    async function carregarPainelSetores() {
        try {
            const response = await fetch("http://localhost:8000/api/setores-dashboard", {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const setores = await response.json();
            
            tabelaSetores.innerHTML = "";
            setores.forEach(s => {
                const tr = document.createElement("tr");
                tr.className = "clickable-row";
                tr.innerHTML = `
                    <td>${s.nome}</td>
                    <td><strong>${s.sigla}</strong></td>
                    <td>${s.total_funcionarios}</td>
                    <td><span class="badge badge-aberto">${s.chamados_abertos}</span></td>
                    <td><span class="badge badge-progresso">${s.chamados_andamento}</span></td>
                    <td><span class="badge badge-fechado">${s.chamados_fechados}</span></td>
                    <td>
                        <button class="btn-edit-setor" data-id="${s.id}" data-nome="${s.nome}" data-sigla="${s.sigla}" ${perfilLogado === 'Gestor' ? 'disabled' : ''}>Editar</button>
                    </td>
                `;
                
                // Evento ao clicar na linha para listar os chamados
                tr.addEventListener("click", (e) => {
                    if (e.target.tagName !== 'BUTTON') {
                        verChamadosDoSetor(s.id, s.nome);
                    }
                });

                tabelaSetores.appendChild(tr);
            });

            document.querySelectorAll(".btn-edit-setor").forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.stopPropagation();
                    abrirModal(e.target.dataset);
                });
            });
        } catch (error) {
            console.error(error);
        }
    }

    async function verChamadosDoSetor(setorId, nomeSetor) {
        try {
            const response = await fetch(`http://localhost:8000/api/setores/${setorId}/chamados`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const chamados = await response.json();
            
            tituloChamados.textContent = `Chamados do Setor: ${nomeSetor}`;
            tabelaChamados.innerHTML = "";
            
            if (chamados.length === 0) {
                tabelaChamados.innerHTML = `<tr><td colspan="4" style="text-align:center;">Nenhum chamado registrado neste setor.</td></tr>`;
            } else {
                chamados.forEach(c => {
                    const dataFormatada = new Date(c.data_criacao).toLocaleString('pt-BR');
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${c.titulo}</td>
                        <td>${c.prioridade}</td>
                        <td>${c.status}</td>
                        <td>${dataFormatada}</td>
                    `;
                    tabelaChamados.appendChild(tr);
                });
            }
            painelChamados.classList.add("active");
        } catch (error) {
            console.error(error);
        }
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const id = document.getElementById("setorId").value;
        const url = id ? `http://localhost:8000/api/setores/${id}` : "http://localhost:8000/api/setores";
        const method = id ? "PUT" : "POST";

        const payload = {
            nome: document.getElementById("nome").value,
            sigla: document.getElementById("sigla").value.toUpperCase()
        };

        const response = await fetch(url, {
            method: method,
            headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            fecharModal();
            carregarPainelSetores();
        }
    });
});
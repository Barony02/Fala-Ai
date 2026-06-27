document.addEventListener("DOMContentLoaded", () => {
    const perfilLogado = sessionStorage.getItem("perfil");
    const token = localStorage.getItem("token");

    if (perfilLogado !== "Gestor" && perfilLogado !== "Administrador") {
        window.location.href = "/app/dashboard.html";
        return;
    }

    document.getElementById("info-perfil").textContent = `Painel Administrativo • Perfil: ${perfilLogado}`;
    if (perfilLogado === "Gestor") {
        const optAdmin = document.getElementById("opt-admin");
        if (optAdmin) optAdmin.remove();
    }

    let listaUsuariosOriginal = [];
    let direcaoOrdenacao = { id: true, nome: true, email: true, perfil: true, setor_sigla: true };
    let colunaAtiva = '';

    const modal = document.getElementById("modalForm");
    const form = document.getElementById("userForm");
    const tabelaUsuarios = document.getElementById("tabela-usuarios");
    const inputBusca = document.getElementById("filtro-busca");
    const formTitle = document.getElementById("form-title");
    const btnSalvar = document.getElementById("btn-salvar");
    const senhaContainer = document.getElementById("senha-container");
    const inputSenha = document.getElementById("senha");
    const selectSetor = document.getElementById("setor"); // Mapeia o novo select

    // Dispara a carga de usuários e setores em paralelo
    carregarSetores().then(() => {
        carregarUsuarios();
    });

    document.getElementById("btn-abrir-cadastro").addEventListener("click", () => abrirModal());
    document.getElementById("btn-fechar-modal").addEventListener("click", () => fecharModal());
    document.getElementById("btn-cancelar-modal").addEventListener("click", () => fecharModal());

    // Nova função para buscar setores do backend
    async function carregarSetores() {
        try {
            const response = await fetch("http://localhost:8000/api/setores", {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (!response.ok) throw new Error();
            
            const setores = await response.json();
            
            selectSetor.innerHTML = '<option value="" disabled selected>Selecione um setor...</option>';
            
            setores.forEach(s => {
                const option = document.createElement("option");
                option.value = s.sigla;
                option.textContent = `${s.nome} (${s.sigla})`;
                selectSetor.appendChild(option);
            });

            // REGRA DE SEGURANÇA PARA O GESTOR:
            // Se for gestor, trava o select no setor dele após carregar a lista de usuários
            if (perfilLogado === "Gestor" && listaUsuariosOriginal.length > 0) {
                // Pega o setor de qualquer usuário da lista (já que o backend filtrada apenas os do setor dele)
                const setorDoGestor = listaUsuariosOriginal[0].setor_sigla;
                if (setorDoGestor) {
                    selectSetor.value = setorDoGestor;
                    selectSetor.disabled = true; // Impede o gestor de mudar o campo
                }
            }
        } catch (error) {
            exibirMensagem("Falha ao carregar lista de setores.", "var(--danger)");
        }
    }

    // Substitua APENAS essa função no seu /js/gerenciar-usuarios.js
    function abrirModal(dados = null) {
        if (dados) {
            formTitle.textContent = `Editar Usuário ID: ${dados.id}`;
            btnSalvar.textContent = "Salvar Alterações";
            senhaContainer.style.display = "none";
            inputSenha.removeAttribute("required");

            document.getElementById("userId").value = dados.id;
            document.getElementById("nome").value = dados.nome;
            document.getElementById("email").value = dados.email;
            document.getElementById("perfil").value = dados.perfil;
            selectSetor.value = dados.setor;
        } else {
            formTitle.textContent = "Cadastrar Novo Usuário";
            btnSalvar.textContent = "Cadastrar";
            senhaContainer.style.display = "block";
            inputSenha.setAttribute("required", "required");
            form.reset();
            document.getElementById("userId").value = "";
            
            // Se for gestor, reaplica a trava do setor ao abrir o formulário de cadastro limpo
            if (perfilLogado === "Gestor" && listaUsuariosOriginal.length > 0) {
                selectSetor.value = listaUsuariosOriginal[0].setor_sigla;
                selectSetor.disabled = true;
            } else {
                selectSetor.disabled = false; // Admin pode escolher qualquer um
            }
        }
        modal.classList.add("active");
    }

    function fecharModal() {
        modal.classList.remove("active");
        form.reset();
        selectSetor.disabled = false; // Reseta o estado do campo para não quebrar o envio do formulário
    }

    inputBusca.addEventListener("input", () => {
        filtrarERenderizar();
    });

    document.querySelectorAll("th[data-coluna]").forEach(th => {
        th.addEventListener("click", () => {
            const coluna = th.getAttribute("data-coluna");
            ordenarPor(coluna);
        });
    });

    async function carregarUsuarios() {
        try {
            const response = await fetch("http://localhost:8000/api/usuarios", {
                method: "GET",
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (!response.ok) throw new Error();
            
            listaUsuariosOriginal = await response.json();
            filtrarERenderizar();
        } catch (error) {
            exibirMensagem("Falha ao carregar lista de usuários.", "var(--danger)");
        }
    }

    function filtrarERenderizar() {
        const termo = inputBusca.value.toLowerCase().trim();
        
        let dadosFiltrados = listaUsuariosOriginal.filter(user => {
            return (
                user.id.toString().includes(termo) ||
                user.nome.toLowerCase().includes(termo) ||
                user.email.toLowerCase().includes(termo) ||
                user.perfil.toLowerCase().includes(termo) ||
                (user.setor_sigla && user.setor_sigla.toLowerCase().includes(termo))
            );
        });

        renderizarTabela(dadosFiltrados);
    }

    function renderizarTabela(dados) {
        tabelaUsuarios.innerHTML = "";
        dados.forEach(user => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td><strong>#${user.id}</strong></td>
                <td>${user.nome}</td>
                <td>${user.email}</td>
                <td>${user.perfil}</td>
                <td>${user.setor_sigla || "—"}</td>
                <td>
                    <button class="btn-edit" data-id="${user.id}" data-nome="${user.nome}" data-email="${user.email}" data-perfil="${user.perfil}" data-setor="${user.setor_sigla}">Editar</button>
                </td>
            `;
            tabelaUsuarios.appendChild(tr);
        });

        document.querySelectorAll(".btn-edit").forEach(btn => {
            btn.addEventListener("click", (e) => abrirModal(e.target.dataset));
        });
    }

    function ordenarPor(coluna) {
        colunaAtiva = coluna;
        const crescente = direcaoOrdenacao[coluna];
        direcaoOrdenacao[coluna] = !crescente;

        listaUsuariosOriginal.sort((a, b) => {
            let valA = a[coluna];
            let valB = b[coluna];

            if (typeof valA === 'string') {
                return crescente ? valA.localeCompare(valB) : valB.localeCompare(valA);
            } else {
                return crescente ? valA - valB : valB - valA;
            }
        });

        document.querySelectorAll("th[data-coluna]").forEach(th => {
            const seta = th.querySelector(".sort-arrow");
            if (th.getAttribute("data-coluna") === coluna) {
                seta.innerHTML = crescente ? "▲" : "▼";
            } else {
                seta.innerHTML = "";
            }
        });

        filtrarERenderizar();
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userId = document.getElementById("userId").value;
        const isEditing = !!userId;

        const url = isEditing ? `http://localhost:8000/api/usuarios/${userId}` : "http://localhost:8000/api/usuarios";
        const method = isEditing ? "PUT" : "POST";

        const payload = {
            nome: document.getElementById("nome").value,
            email: document.getElementById("email").value,
            perfil: document.getElementById("perfil").value,
            setor_sigla: selectSetor.value // Captura o valor selecionado no dropdown
        };

        if (!isEditing) payload.senha = inputSenha.value;

        try {
            const response = await fetch(url, {
                method: method,
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                exibirMensagem(isEditing ? "Usuário atualizado!" : "Usuário cadastrado com sucesso!", "var(--success)");
                fecharModal();
                carregarUsuarios();
            } else {
                const err = await response.json();
                exibirMensagem(err.detail || "Erro na operação.", "var(--danger)");
            }
        } catch (error) {
            exibirMensagem("Falha ao salvar dados.", "var(--danger)");
        }
    });

    function exibirMensagem(texto, cor) {
        const msg = document.getElementById("mensagem");
        msg.textContent = texto;
        msg.style.color = cor;
        setTimeout(() => msg.textContent = "", 4000);
    }
});
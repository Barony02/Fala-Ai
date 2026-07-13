const API_URL = window.location.hostname === 'localhost'
    ? "http://localhost:8000/api"
    : `${window.location.protocol}//${window.location.hostname}:8000/api`;
const STATUS_ALIASES = {
    "Aberto": "Aberto",
    "Em Progresso": "Em Atendimento",
    "Em Andamento": "Em Atendimento",
    "Em Atendimento": "Em Atendimento",
    "Pausado": "Pausado",
    "Fechado": "Concluído",
    "Concluido": "Concluído",
    "Concluído": "Concluído",
    "Resolvido": "Concluído"
};
const normalizarStatus = (status) => STATUS_ALIASES[status] || status || "Aberto";

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    
    if (!token) {
        window.location.href = "/index.html";
        return;
    }

    const statusFilter = document.getElementById('statusFilter');
    const tbody = document.getElementById('chamadosTableBody');
    const btnPrevPage = document.getElementById('btnPrevPage');
    const btnNextPage = document.getElementById('btnNextPage');
    const pageInfo = document.getElementById('pageInfo');
    
    // Elementos do Modal
    const modal = document.getElementById("chamadoModal");
    const closeButton = document.querySelector(".close-button");
    
    let chamadosLista = []; // Guarda os dados vindos do banco
    let chamadoSelecionado = null;
    let paginaAtual = 1;
    let totalPaginas = 1;
    const itensPorPagina = 10;

    async function carregarChamados() {
        const status = statusFilter.value;
        let url = `${API_URL}/meus-chamados?page=${paginaAtual}&per_page=${itensPorPagina}`;

        if (status) {
            url += `&status=${encodeURIComponent(status)}`;
        }

        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }

            const payload = await response.json();
            chamadosLista = payload.items || payload;
            totalPaginas = payload.total_pages || 1;
            tbody.innerHTML = '';
            atualizarPaginacao();

            if (chamadosLista.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #666;">Nenhum chamado encontrado.</td></tr>`;
                return;
            }

            chamadosLista.forEach(chamado => {
                const tr = document.createElement('tr');
                tr.style.cursor = "pointer"; // Indica que a linha é clicável
                tr.title = "Clique para ver detalhes";
                
                const statusNormalizado = normalizarStatus(chamado.status);
                let statusClass = 'status-aberto';
                if (statusNormalizado === 'Em Atendimento') statusClass = 'status-progresso';
                if (statusNormalizado === 'Pausado') statusClass = 'status-pausado';
                if (statusNormalizado === 'Concluído') statusClass = 'status-fechado';

                const dataFormatada = chamado.data_criacao 
                    ? new Date(chamado.data_criacao).toLocaleDateString('pt-BR') 
                    : '-';

                tr.innerHTML = `
                    <td>${chamado.id}</td>
                    <td><strong>${chamado.titulo}</strong></td>
                    <td><span class="status-badge ${statusClass}">${statusNormalizado}</span></td>
                    <td>${chamado.prioridade}</td>
                    <td>${dataFormatada}</td>
                `;

                // Evento que abre os detalhes ao clicar na linha
                tr.addEventListener('click', () => abrirDetalhesModal(chamado.id));

                tbody.appendChild(tr);
            });
        } catch (error) {
            console.error("Erro ao carregar chamados:", error);
            tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #dc2626;">Erro ao carregar dados do banco.</td></tr>`;
        }
    }

    function atualizarPaginacao() {
        pageInfo.textContent = `Página ${paginaAtual} de ${totalPaginas}`;
        btnPrevPage.disabled = paginaAtual <= 1;
        btnNextPage.disabled = paginaAtual >= totalPaginas;
    }

    async function abrirDetalhesModal(id) {
        try {
            const response = await fetch(`${API_URL}/chamados/${id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) throw new Error("Erro ao carregar chamado");
            chamadoSelecionado = await response.json();
        } catch (e) {
            const chamado = chamadosLista.find(c => c.id === id);
            if (!chamado) return;
            chamadoSelecionado = chamado;
        }

        const chamado = chamadoSelecionado;

        // Injeta os dados no modal
        document.getElementById("modalId").textContent = chamado.id;
        document.getElementById("modalTitulo").textContent = chamado.titulo;
        document.getElementById("modalPrioridade").textContent = chamado.prioridade;
        document.getElementById("modalSetor").textContent = chamado.setor_responsavel?.nome || chamado.setor_responsavel || "Não informado";
        document.getElementById("modalResponsavel").textContent = chamado.usuario_responsavel?.nome || chamado.usuario_responsavel || "Enviar para todos (Nenhum específico)";
        document.getElementById("modalDescricao").textContent = chamado.descricao;
        
        const dataCompleta = chamado.data_criacao 
            ? new Date(chamado.data_criacao).toLocaleString('pt-BR') 
            : '-';
        document.getElementById("modalData").textContent = dataCompleta;

        // Gerencia classes de status no modal
        const statusSpan = document.getElementById("modalStatus");
        const statusNormalizado = normalizarStatus(chamado.status);
        statusSpan.textContent = statusNormalizado;
        statusSpan.className = "status-badge";
        if (statusNormalizado === 'Aberto') statusSpan.classList.add('status-aberto');
        if (statusNormalizado === 'Em Atendimento') statusSpan.classList.add('status-progresso');
        if (statusNormalizado === 'Pausado') statusSpan.classList.add('status-pausado');
        if (statusNormalizado === 'Concluído') statusSpan.classList.add('status-fechado');

        renderizarAnexos(chamado.anexos || []);
        configurarAcoesConclusao(chamado);

        // Exibe o modal
        modal.style.display = "block";
    }

    function mostrarMensagemModal(texto, tipo = "sucesso") {
        if (texto && window.falaAiToast) {
            window.falaAiToast(texto, tipo);
        }
        const el = document.getElementById("modalMensagem");
        if (!el) return;
        el.textContent = texto;
        el.className = `mensagem ${tipo}`;
        setTimeout(() => {
            el.textContent = "";
            el.className = "mensagem";
        }, 4000);
    }

    function formatarTamanho(bytes) {
        if (!bytes) return "0 KB";
        if (bytes < 1024 * 1024) return `${Math.ceil(bytes / 1024)} KB`;
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    }

    function renderizarAnexos(anexos) {
        const lista = document.getElementById("modalAnexos");
        if (!lista) return;
        if (!anexos.length) {
            lista.innerHTML = '<div class="attachment-item">Nenhum anexo enviado.</div>';
            return;
        }
        lista.innerHTML = "";
        anexos.forEach(anexo => {
            const div = document.createElement("div");
            div.className = "attachment-item";
            div.innerHTML = `
                <span>${anexo.nome_original}<br><small>${formatarTamanho(anexo.tamanho)}</small></span>
                <button type="button">Baixar</button>
            `;
            div.querySelector("button").addEventListener("click", () => baixarAnexo(anexo));
            lista.appendChild(div);
        });
    }

    async function baixarAnexo(anexo) {
        const response = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}/anexos/${anexo.id}/download`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) {
            mostrarMensagemModal("Não foi possível baixar o anexo.", "erro");
            return;
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = anexo.nome_original;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    function configurarAcoesConclusao(chamado) {
        const statusNormalizado = normalizarStatus(chamado.status);
        const bloco = document.getElementById("acoesConclusao");
        const avaliacaoAtual = document.getElementById("avaliacaoAtual");
        const formAvaliacao = document.getElementById("formAvaliacao");
        const formReabertura = document.getElementById("formReabertura");
        const prazoEl = document.getElementById("prazoReabertura");
        if (!bloco) return;

        bloco.style.display = statusNormalizado === "Concluído" ? "block" : "none";
        if (statusNormalizado !== "Concluído") return;

        if (chamado.avaliacao) {
            avaliacaoAtual.textContent = `Avaliado com nota ${chamado.avaliacao.nota}/5${chamado.avaliacao.comentario ? ` - ${chamado.avaliacao.comentario}` : ""}`;
            formAvaliacao.style.display = "none";
        } else {
            avaliacaoAtual.textContent = "";
            formAvaliacao.style.display = "flex";
        }

        const prazo = chamado.prazo_reabertura ? new Date(chamado.prazo_reabertura) : null;
        const dentroPrazo = prazo && new Date() <= prazo;
        formReabertura.style.display = dentroPrazo ? "flex" : "none";
        prazoEl.textContent = prazo
            ? `Prazo para reabertura: ${prazo.toLocaleString("pt-BR")}`
            : "";
    }

    async function recarregarChamadoSelecionado() {
        if (!chamadoSelecionado) return;
        await abrirDetalhesModal(chamadoSelecionado.id);
    }

    // Fechar modal ao clicar no (X) ou fora dele
    closeButton.addEventListener("click", () => modal.style.display = "none");
    window.addEventListener("click", (event) => {
        if (event.target === modal) modal.style.display = "none";
    });

    statusFilter.addEventListener('change', () => {
        paginaAtual = 1;
        carregarChamados();
    });
    btnPrevPage.addEventListener('click', () => {
        if (paginaAtual > 1) {
            paginaAtual--;
            carregarChamados();
        }
    });
    btnNextPage.addEventListener('click', () => {
        if (paginaAtual < totalPaginas) {
            paginaAtual++;
            carregarChamados();
        }
    });

    document.getElementById("btnEnviarAnexoSolicitante")?.addEventListener("click", async () => {
        if (!chamadoSelecionado) return;
        const input = document.getElementById("inputAnexoSolicitante");
        const arquivo = input?.files?.[0];
        if (!arquivo) {
            mostrarMensagemModal("Selecione um arquivo para enviar.", "erro");
            return;
        }
        const formData = new FormData();
        formData.append("arquivo", arquivo);
        const response = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}/anexos`, {
            method: "POST",
            headers: { 'Authorization': `Bearer ${token}` },
            body: formData
        });
        if (response.ok) {
            input.value = "";
            mostrarMensagemModal("Anexo enviado.", "sucesso");
            await recarregarChamadoSelecionado();
        } else {
            const erro = await response.json().catch(() => ({}));
            mostrarMensagemModal(erro.detail || "Erro ao enviar anexo.", "erro");
        }
    });

    document.getElementById("btnAvaliarChamado")?.addEventListener("click", async () => {
        if (!chamadoSelecionado) return;
        const nota = parseInt(document.getElementById("selectNota").value, 10);
        const comentario = document.getElementById("comentarioAvaliacao").value.trim();
        if (!nota) {
            mostrarMensagemModal("Selecione uma nota para avaliar.", "erro");
            return;
        }
        const response = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}/avaliacao`, {
            method: "POST",
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ nota, comentario })
        });
        if (response.ok) {
            document.getElementById("selectNota").value = "";
            document.getElementById("comentarioAvaliacao").value = "";
            mostrarMensagemModal("Avaliação registrada.", "sucesso");
            await recarregarChamadoSelecionado();
        } else {
            const erro = await response.json().catch(() => ({}));
            mostrarMensagemModal(erro.detail || "Erro ao avaliar chamado.", "erro");
        }
    });

    document.getElementById("btnReabrirChamado")?.addEventListener("click", async () => {
        if (!chamadoSelecionado) return;
        const justificativa = document.getElementById("justificativaReabertura").value.trim();
        if (!justificativa) {
            mostrarMensagemModal("Informe a justificativa da reabertura.", "erro");
            return;
        }
        const response = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}/reabrir`, {
            method: "POST",
            headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ justificativa })
        });
        if (response.ok) {
            document.getElementById("justificativaReabertura").value = "";
            mostrarMensagemModal("Chamado reaberto.", "sucesso");
            await carregarChamados();
            await recarregarChamadoSelecionado();
        } else {
            const erro = await response.json().catch(() => ({}));
            mostrarMensagemModal(erro.detail || "Erro ao reabrir chamado.", "erro");
        }
    });
    carregarChamados();
});

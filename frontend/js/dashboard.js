console.log("dashboard.js carregado com controle de fuso e sem busca!");

const API_URL = `http://${window.location.hostname}:8000/api`;
const PESO_PRIORIDADE = { "Alta": 3, "Média": 2, "Baixa": 1 };
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
const STATUS_CONFIG = {
    "Aberto": { cards: "cards-Aberto", count: "count-Aberto" },
    "Em Atendimento": { cards: "cards-Atendimento", count: "count-Atendimento" },
    "Pausado": { cards: "cards-Pausado", count: "count-Pausado" },
    "Concluído": { cards: "cards-Concluido", count: "count-Concluido" }
};

const getToken = () => localStorage.getItem("token") || localStorage.getItem("access_token");
const normalizarStatus = (status) => STATUS_ALIASES[status] || status || "Aberto";

function mostrarMensagemDashboard(texto, tipo = "info") {
    const modalMensagem = document.getElementById("modalMensagem");
    if (!modalMensagem) {
        alert(texto);
        return;
    }
    modalMensagem.textContent = texto;
    modalMensagem.className = `mensagem ${tipo}`;
    setTimeout(() => {
        modalMensagem.textContent = "";
        modalMensagem.className = "mensagem";
    }, 4000);
}

window.allowDrop = (ev) => ev.preventDefault();

window.drag = (ev, chamadoId) => {
    ev.dataTransfer.setData("text/plain", chamadoId);
    document.getElementById(`card-${chamadoId}`)?.classList.add("dragging");
};

window.drop = async (ev) => {
    ev.preventDefault();
    const chamadoId = ev.dataTransfer.getData("text/plain");
    document.getElementById(`card-${chamadoId}`)?.classList.remove("dragging");

    const targetColumn = ev.target.closest(".kanban-column");
    if (!targetColumn) return;
    
    const novoStatus = normalizarStatus(targetColumn.getAttribute("data-status"));
    const chamadoLocal = filaOriginal.find(c => c.id == chamadoId);
    let responsavelAlvoId = chamadoLocal ? (chamadoLocal.usuario_responsavel?.id || chamadoLocal.usuario_responsavel_id) : null;

    if (novoStatus === "Em Atendimento" && (!responsavelAlvoId || responsavelAlvoId === 0)) {
        responsavelAlvoId = usuarioLogado.id;
    }

    try {
        const res = await fetch(`${API_URL}/chamados/${chamadoId}`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${getToken()}`, "Content-Type": "application/json" },
            body: JSON.stringify({ status: novoStatus, usuario_responsavel_id: responsavelAlvoId, justificativa: "Atualização via fluxo Kanban." })
        });
        
        if (res.ok) window.dispatchEvent(new CustomEvent("refreshKanban"));
        else mostrarMensagemDashboard((await res.json()).detail || "Não autorizado", "erro");
    } catch (e) { console.error(e); }
};

let filaOriginal = [], chamadoSelecionado = null, filtroAtivo = "todos";
let usuarioLogado = { id: null, setorId: null };

document.addEventListener("DOMContentLoaded", () => {
    const token = getToken();
    if (!token) { window.location.href = "/index.html"; return; }
    
    try {
        usuarioLogado.id = parseInt(JSON.parse(window.atob(token.split('.')[1])).sub);
    } catch (e) { console.error("JWT Error", e); }

    const modal = document.getElementById("actionModal");
    const closeButton = document.querySelector(".close-button");

    function mostrarMensagemModal(texto, tipo = "info") {
        mostrarMensagemDashboard(texto, tipo);
    }

    window.addEventListener("refreshKanban", () => buscarFilaDoSetor());

    async function init() {
        try {
            let res = await fetch(`${API_URL}/usuarios`, { headers: { "Authorization": `Bearer ${token}` } });
            if (res.ok) {
                const dadosUsuarios = await res.json().catch(() => null);
                if (dadosUsuarios) {
                    const eu = dadosUsuarios.find(u => u.id === usuarioLogado.id);
                    if (eu) usuarioLogado.setorId = eu.setor_id;
                }
            }
            
            if (!usuarioLogado.setorId) {
                let resMe = await fetch(`${API_URL}/usuarios/perfil/me`, { headers: { "Authorization": `Bearer ${token}` } });
                if (resMe.ok) {
                    let perfilData = await resMe.json();
                    usuarioLogado.setorId = perfilData.setor_id || 1; 
                }
            }

            await buscarFilaDoSetor();
            await carregarSetoresTransferencia();
        } catch (e) { console.error(e); }
    }

    async function buscarFilaDoSetor() {
        if (!usuarioLogado.setorId) return;
        try {
            // Aponta para a nova rota isolada do dashboard
            const res = await fetch(`${API_URL}/setores/${usuarioLogado.setorId}/chamados-dashboard`, { 
                headers: { "Authorization": `Bearer ${token}` } 
            });
            if (res.ok) { filaOriginal = await res.json(); filtrarOrdenarERenderizar(); }
        } catch (e) { console.error(e); }
    }
    
    const getIdResponsavel = (c) => c.usuario_responsavel?.id || c.usuario_responsavel_id || null;

    function filtrarOrdenarERenderizar() {
        let dados = [...filaOriginal];
        if (filtroAtivo === "disponiveis") dados = dados.filter(c => !getIdResponsavel(c) && normalizarStatus(c.status) === "Aberto");
        else if (filtroAtivo === "meus") dados = dados.filter(c => getIdResponsavel(c) === usuarioLogado.id);

        dados.sort((a, b) => {
            const diff = (PESO_PRIORIDADE[b.prioridade] || 0) - (PESO_PRIORIDADE[a.prioridade] || 0);
            if (diff !== 0) return diff;
            return new Date(a.data_criacao || 0) - new Date(b.data_criacao || 0);
        });

        renderizarKanban(dados);
    }

    function renderizarKanban(lista) {
        const colunas = Object.fromEntries(
            Object.entries(STATUS_CONFIG).map(([status, cfg]) => [status, document.getElementById(cfg.cards)])
        );
        if (!colunas["Aberto"]) return;

        Object.values(colunas).forEach(el => { if (el) el.innerHTML = ""; });
        const contadores = { "Aberto": 0, "Em Atendimento": 0, "Pausado": 0, "Concluído": 0 };

        lista.forEach(c => {
            const status = normalizarStatus(c.status);
            if (!colunas[status]) return;
            contadores[status]++;

            const card = document.createElement("div");
            card.className = "kanban-card";
            card.id = `card-${c.id}`;
            card.setAttribute("draggable", "true");
            card.addEventListener("dragstart", (e) => window.drag(e, c.id));
            card.addEventListener("dragend", () => card.classList.remove("dragging"));

            const dataStr = c.data_criacao ? new Date(c.data_criacao).toLocaleDateString('pt-BR') : '-';
            const idResp = getIdResponsavel(c);
            const respTxt = idResp === usuarioLogado.id ? "Comigo" : (c.usuario_responsavel?.nome || (idResp ? `Técnico #${idResp}` : "Aberto (Nenhum)"));
            const sla = c.sla || {};
            const slaEstado = sla.estado || "no_prazo";
            const slaTexto = sla.estado === "concluido"
                ? `SLA ${sla.percentual || 0}%`
                : `${sla.horas_decorridas || 0}h/${sla.prazo_horas || "-"}h`;

            card.innerHTML = `
                <div class="card-body-click">
                    <div class="card-top">
                        <div class="card-title">#${c.id} - ${c.titulo}</div>
                        <span class="prio-badge" data-prio="${c.prioridade || 'Média'}">${c.prioridade || '-'}</span>
                    </div>
                    <div class="card-desc">${c.descricao}</div>
                </div>
                <div class="card-footer">
                    <span><i class="fa-solid fa-user"></i> ${respTxt}</span>
                    <span><i class="fa-solid fa-calendar"></i> ${dataStr}</span>
                </div>
                <div class="card-footer">
                    <span class="sla-pill sla-${slaEstado}">${slaTexto}</span>
                    <span>${status}</span>
                </div>
            `;

            card.addEventListener("click", () => {
                if (!card.classList.contains("dragging")) abrirPainelAcoes(c.id);
            });
            colunas[status].appendChild(card);
        });

        Object.keys(contadores).forEach(st => {
            const el = document.getElementById(STATUS_CONFIG[st].count);
            if (el) el.textContent = contadores[st];
        });
    }

    async function abrirPainelAcoes(id) {
        try {
            const res = await fetch(`${API_URL}/chamados/${id}`, { headers: { "Authorization": `Bearer ${token}` } });
            if (!res.ok) return;
            chamadoSelecionado = await res.json();

            document.getElementById("modalId").textContent = chamadoSelecionado.id || '';
            document.getElementById("modalTitulo").textContent = chamadoSelecionado.titulo || '';
            document.getElementById("modalDescricao").textContent = chamadoSelecionado.descricao || '';
            document.getElementById("modalSolicitante").textContent = chamadoSelecionado.usuario_solicitante?.nome || `ID ${chamadoSelecionado.usuario_solicitante_id || '-'}`;
            document.getElementById("modalSetorOrigem").textContent = chamadoSelecionado.setor_solicitante ? `${chamadoSelecionado.setor_solicitante.sigla} - ${chamadoSelecionado.setor_solicitante.nome}` : "Não informado";
            document.getElementById("modalResponsavel").textContent = chamadoSelecionado.usuario_responsavel?.nome || "Disponível para a equipe (Nenhum)";
            document.getElementById("modalStatusAtual").textContent = normalizarStatus(chamadoSelecionado.status);
            document.getElementById("modalDataCriacao").textContent = chamadoSelecionado.data_criacao ? new Date(chamadoSelecionado.data_criacao).toLocaleString('pt-BR') : '-';
            document.getElementById("modalDataAtualizacao").textContent = chamadoSelecionado.data_atualizacao ? new Date(chamadoSelecionado.data_atualizacao).toLocaleString('pt-BR') : 'Sem modificações';
            const sla = chamadoSelecionado.sla || {};
            document.getElementById("modalSla").textContent = `${sla.horas_decorridas || 0}h de ${sla.prazo_horas || "-"}h (${sla.percentual || 0}%)`;

            const btn = document.getElementById("btnAtribuir");
            if (btn) {
                const ehMeu = getIdResponsavel(chamadoSelecionado) === usuarioLogado.id;
                btn.textContent = ehMeu ? "Liberar Chamado" : "Assumir Chamado";
                btn.className = `btn-action ${ehMeu ? 'btn-danger' : 'btn-primary'}`;
            }
            if (modal) modal.style.display = "block";
            renderizarTemposSetor(chamadoSelecionado.tempos_por_setor || []);
            await carregarHistorico(id);
        } catch (e) { console.error(e); }
    }

    function formatarHoras(valor) {
        if (valor === null || valor === undefined) return "-";
        return `${Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 2 })}h`;
    }

    function renderizarTemposSetor(tempos) {
        const lista = document.getElementById("listaTemposSetor");
        if (!lista) return;
        if (!tempos.length) {
            lista.innerHTML = '<div class="sector-timer-item">Nenhum tempo registrado ainda.</div>';
            return;
        }

        lista.innerHTML = "";
        tempos.forEach(item => {
            const div = document.createElement("div");
            div.className = "sector-timer-item";
            const setor = item.setor || {};
            const situacao = item.resolvido ? "Resolvido neste setor" : (item.transferido ? "Transferido" : "Em andamento");
            div.innerHTML = `
                <strong>${setor.sigla || "-"} - ${setor.nome || "Setor"} • ${situacao}</strong>
                <div class="timer-metrics">
                    <div class="timer-metric"><span>Resposta</span><b>${formatarHoras(item.tempo_resposta_horas)}</b></div>
                    <div class="timer-metric"><span>Resolução</span><b>${formatarHoras(item.tempo_resolucao_horas)}</b></div>
                    <div class="timer-metric"><span>Total</span><b>${formatarHoras(item.tempo_total_horas)}</b></div>
                </div>
            `;
            lista.appendChild(div);
        });
    }

    async function carregarHistorico(id) {
        const lista = document.getElementById("listaHistorico");
        if (!lista) return;
        lista.innerHTML = '<div class="history-item">Carregando histórico...</div>';
        try {
            const res = await fetch(`${API_URL}/chamados/${id}/historico`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            if (!res.ok) throw new Error("Erro ao carregar histórico");
            const historico = await res.json();
            if (!historico.length) {
                lista.innerHTML = '<div class="history-item">Nenhum registro ainda.</div>';
                return;
            }
            lista.innerHTML = "";
            historico.forEach(item => {
                const div = document.createElement("div");
                div.className = "history-item";
                const data = item.data_criacao ? new Date(item.data_criacao).toLocaleString("pt-BR") : "-";
                const detalhe = item.tipo === "Nota"
                    ? item.comentario
                    : `${item.valor_anterior || item.setor_origem?.nome || "-"} -> ${item.valor_novo || item.setor_destino?.nome || "-"}`;
                div.innerHTML = `<strong>${item.tipo} • ${item.autor?.nome || "Equipe"} • ${data}</strong><span>${detalhe || ""}</span>`;
                lista.appendChild(div);
            });
        } catch (e) {
            lista.innerHTML = '<div class="history-item">Não foi possível carregar o histórico.</div>';
        }
    }

    document.getElementById("btnAtribuir")?.replaceWith(document.getElementById("btnAtribuir").cloneNode(true));


    document.getElementById("btnAtribuir")?.addEventListener("click", async () => {
        const idResp = chamadoSelecionado.usuario_responsavel?.id || chamadoSelecionado.usuario_responsavel_id;
        const ehMeu = idResp === usuarioLogado.id;
        
        const token = getToken();
        const modal = document.getElementById("actionModal");

        try {
            const res = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}`, {
                method: "PUT",
                headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    usuario_responsavel_id: ehMeu ? null : usuarioLogado.id, 
                    status: ehMeu ? "Aberto" : "Em Atendimento",
                    justificativa: ehMeu ? "Liberando chamado do técnico." : "Assumindo chamado pendente." 
                })
            });
            if (res.ok) {
                if (modal) modal.style.display = "none";
                buscarFilaDoSetor();
            } else {
                const err = await res.json();
                mostrarMensagemModal(err.detail || "Não autorizado", "erro");
            }
        } catch (e) { console.error(e); }
    });

    async function carregarSetoresTransferencia() {
        const select = document.getElementById("selectSetorDestino");
        if (!select) return;
        try {
            const res = await fetch(`${API_URL}/setores`, { headers: { "Authorization": `Bearer ${token}` } });
            if (res.ok) {
                (await res.json()).forEach(s => {
                    if (s.id !== usuarioLogado.setorId) {
                        const opt = document.createElement("option");
                        opt.value = s.id; opt.textContent = s.nome;
                        select.appendChild(opt);
                    }
                });
            }
        } catch (e) {}
    }

    document.getElementById("btnTransferir")?.addEventListener("click", async () => {
        const destino = document.getElementById("selectSetorDestino").value;
        const justificativa = document.getElementById("txtJustificativaTransferencia").value.trim();
        if (!destino || !justificativa) { alert("Preencha o destino e o motivo."); return; }

        try {
            const res = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}/transferencia`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
                body: JSON.stringify({ setor_destino_id: parseInt(destino), justificativa })
            });
            if (res.ok) {
                if (modal) modal.style.display = "none";
                buscarFilaDoSetor();
                document.getElementById("txtJustificativaTransferencia").value = "";
            } else {
                mostrarMensagemModal((await res.json()).detail || "Erro ao transferir", "erro");
            }
        } catch (e) { console.error(e); }
    });

    document.getElementById("btnSalvarNota")?.addEventListener("click", async () => {
        if (!chamadoSelecionado) return;
        const campo = document.getElementById("txtNotaInterna");
        const comentario = campo.value.trim();
        if (!comentario) {
            mostrarMensagemModal("Digite a nota interna antes de salvar.", "erro");
            return;
        }

        try {
            const res = await fetch(`${API_URL}/chamados/${chamadoSelecionado.id}/notas`, {
                method: "POST",
                headers: { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" },
                body: JSON.stringify({ comentario })
            });
            if (res.ok) {
                campo.value = "";
                mostrarMensagemModal("Nota interna registrada.", "sucesso");
                carregarHistorico(chamadoSelecionado.id);
            } else {
                mostrarMensagemModal((await res.json()).detail || "Erro ao salvar nota", "erro");
            }
        } catch (e) {
            mostrarMensagemModal("Erro ao salvar nota interna.", "erro");
        }
    });

    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");
            filtroAtivo = e.target.getAttribute("data-filter");
            filtrarOrdenarERenderizar();
        });
    });

    closeButton?.addEventListener("click", () => { if (modal) modal.style.display = "none"; });
    
    init();
});

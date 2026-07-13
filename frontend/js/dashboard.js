console.log("dashboard.js carregado com controle de fuso e sem busca!");

const API_URL = `http://${window.location.hostname}:8000/api`;
const PESO_PRIORIDADE = { "Alta": 3, "Média": 2, "Baixa": 1 };

const getToken = () => localStorage.getItem("token") || localStorage.getItem("access_token");

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
    
    const novoStatus = targetColumn.getAttribute("data-status");
    const chamadoLocal = filaOriginal.find(c => c.id == chamadoId);
    let responsavelAlvoId = chamadoLocal ? (chamadoLocal.usuario_responsavel?.id || chamadoLocal.usuario_responsavel_id) : null;

    if (novoStatus === "Em Progresso" && (!responsavelAlvoId || responsavelAlvoId === 0)) {
        responsavelAlvoId = usuarioLogado.id;
    }

    try {
        const res = await fetch(`${API_URL}/chamados/${chamadoId}`, {
            method: "PUT",
            headers: { "Authorization": `Bearer ${getToken()}`, "Content-Type": "application/json" },
            body: JSON.stringify({ status: novoStatus, usuario_responsavel_id: responsavelAlvoId, justificativa: "Atualização via fluxo Kanban." })
        });
        
        if (res.ok) window.dispatchEvent(new CustomEvent("refreshKanban"));
        else alert(`Erro na transição: ${(await res.json()).detail || "Não autorizado"}`);
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
        if (filtroAtivo === "disponiveis") dados = dados.filter(c => !getIdResponsavel(c) && c.status === "Aberto");
        else if (filtroAtivo === "meus") dados = dados.filter(c => getIdResponsavel(c) === usuarioLogado.id);

        dados.sort((a, b) => {
            const diff = (PESO_PRIORIDADE[b.prioridade] || 0) - (PESO_PRIORIDADE[a.prioridade] || 0);
            if (diff !== 0) return diff;
            return new Date(a.data_criacao || 0) - new Date(b.data_criacao || 0);
        });

        renderizarKanban(dados);
    }

    function renderizarKanban(lista) {
        const colunas = { "Aberto": document.getElementById("cards-Aberto"), "Em Progresso": document.getElementById("cards-Progresso"), "Fechado": document.getElementById("cards-Fechado") };
        if (!colunas["Aberto"]) return;

        Object.values(colunas).forEach(el => { if (el) el.innerHTML = ""; });
        const contadores = { "Aberto": 0, "Em Progresso": 0, "Fechado": 0 };

        lista.forEach(c => {
            if (!colunas[c.status]) return;
            contadores[c.status]++;

            const card = document.createElement("div");
            card.className = "kanban-card";
            card.id = `card-${c.id}`;
            card.setAttribute("draggable", "true");
            card.addEventListener("dragstart", (e) => window.drag(e, c.id));
            card.addEventListener("dragend", () => card.classList.remove("dragging"));

            const dataStr = c.data_criacao ? new Date(c.data_criacao).toLocaleDateString('pt-BR') : '-';
            const idResp = getIdResponsavel(c);
            const respTxt = idResp === usuarioLogado.id ? "Comigo" : (c.usuario_responsavel?.nome || (idResp ? `Técnico #${idResp}` : "Aberto (Nenhum)"));

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
            `;

            card.addEventListener("click", () => {
                if (!card.classList.contains("dragging")) abrirPainelAcoes(c.id);
            });
            colunas[c.status].appendChild(card);
        });

        Object.keys(contadores).forEach(st => {
            const el = document.getElementById(`count-${st === "Em Progresso" ? "Progresso" : st}`);
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
            document.getElementById("modalStatusAtual").textContent = chamadoSelecionado.status || '-';
            document.getElementById("modalDataCriacao").textContent = chamadoSelecionado.data_criacao ? new Date(chamadoSelecionado.data_criacao).toLocaleString('pt-BR') : '-';
            document.getElementById("modalDataAtualizacao").textContent = chamadoSelecionado.data_atualizacao ? new Date(chamadoSelecionado.data_atualizacao).toLocaleString('pt-BR') : 'Sem modificações';

            const btn = document.getElementById("btnAtribuir");
            if (btn) {
                const ehMeu = getIdResponsavel(chamadoSelecionado) === usuarioLogado.id;
                btn.textContent = ehMeu ? "Liberar Chamado" : "Assumir Chamado";
                btn.className = `btn-action ${ehMeu ? 'btn-danger' : 'btn-primary'}`;
            }
            if (modal) modal.style.display = "block";
        } catch (e) { console.error(e); }
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
                    status: ehMeu ? "Aberto" : "Em Progresso", 
                    justificativa: ehMeu ? "Liberando chamado do técnico." : "Assumindo chamado pendente." 
                })
            });
            if (res.ok) { 
                if (modal) modal.style.display = "none"; 
                buscarFilaDoSetor(); 
            } else {
                const err = await res.json();
                alert(`Erro na requisição: ${err.detail || "Não autorizado"}`);
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
            }
        } catch (e) { console.error(e); }
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
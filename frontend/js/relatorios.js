const API_URL = window.location.hostname === 'localhost'
    ? "http://localhost:8000/api"
    : `${window.location.protocol}//${window.location.hostname}:8000/api`;

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    const perfil = sessionStorage.getItem("perfil");
    if (!token || (perfil !== "Gestor" && perfil !== "Administrador")) {
        window.location.href = "/app/dashboard.html";
        return;
    }

    const dataInicio = document.getElementById("dataInicio");
    const dataFim = document.getElementById("dataFim");
    const setorFiltro = document.getElementById("setorFiltro");
    const cardsResumo = document.getElementById("cardsResumo");
    const tabela = document.getElementById("tabelaRelatorio");
    const mensagem = document.getElementById("mensagemRelatorio");

    function headers() {
        return { "Authorization": `Bearer ${token}` };
    }

    function montarQuery(formato = "json") {
        const params = new URLSearchParams({ formato });
        if (dataInicio.value) params.set("data_inicio", dataInicio.value);
        if (dataFim.value) params.set("data_fim", dataFim.value);
        if (setorFiltro.value) params.set("setor_id", setorFiltro.value);
        return params.toString();
    }

    function mostrarMensagem(texto, tipo = "sucesso") {
        mensagem.textContent = texto;
        mensagem.className = `mensagem ${tipo}`;
        if (texto && window.falaAiToast && tipo !== "sucesso") {
            window.falaAiToast(texto, tipo);
        }
    }

    async function carregarSetores() {
        const res = await fetch(`${API_URL}/setores`, { headers: headers() });
        if (!res.ok) return;
        const setores = await res.json();
        setores.forEach(setor => {
            const option = document.createElement("option");
            option.value = setor.id;
            option.textContent = setor.nome;
            setorFiltro.appendChild(option);
        });
    }

    function renderizarResumo(resumo) {
        const labels = {
            total: "Total",
            abertos: "Abertos",
            em_atendimento: "Em atendimento",
            pausados: "Pausados",
            concluidos: "Concluídos",
            atrasados: "Atrasados",
            tempo_medio_resposta_horas: "Resposta média (h)",
            media_avaliacao: "Média avaliação",
        };
        cardsResumo.innerHTML = Object.entries(labels).map(([chave, label]) => `
            <article class="summary-card">
                <span>${label}</span>
                <strong>${resumo[chave] ?? "-"}</strong>
            </article>
        `).join("");
    }

    function renderizarTabela(items) {
        if (!items.length) {
            tabela.innerHTML = '<tr><td colspan="7">Nenhum chamado encontrado para os filtros.</td></tr>';
            return;
        }
        tabela.innerHTML = items.map(item => `
            <tr>
                <td>#${item.id}</td>
                <td>${item.titulo}</td>
                <td>${item.status}</td>
                <td>${item.setor_responsavel}</td>
                <td>${item.sla_estado} (${item.sla_percentual}%)</td>
                <td>${item.tempo_resposta_horas ?? "-"}h</td>
                <td>${item.avaliacao_nota ?? "-"}</td>
            </tr>
        `).join("");
    }

    async function carregarRelatorio() {
        try {
            mostrarMensagem("Carregando relatório...", "sucesso");
            const res = await fetch(`${API_URL}/relatorios/gerencial?${montarQuery()}`, { headers: headers() });
            if (!res.ok) throw new Error("Erro ao carregar relatório");
            const dados = await res.json();
            renderizarResumo(dados.resumo);
            renderizarTabela(dados.items);
            mostrarMensagem("");
        } catch (e) {
            mostrarMensagem("Não foi possível carregar o relatório.", "erro");
        }
    }

    async function baixarRelatorio(formato) {
        const res = await fetch(`${API_URL}/relatorios/gerencial?${montarQuery(formato)}`, { headers: headers() });
        if (!res.ok) {
            mostrarMensagem("Erro ao exportar relatório.", "erro");
            return;
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `relatorio-chamados.${formato === "xlsx" ? "xlsx" : "pdf"}`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    document.getElementById("btnAplicarFiltros").addEventListener("click", carregarRelatorio);
    document.getElementById("btnExportarPdf").addEventListener("click", () => baixarRelatorio("pdf"));
    document.getElementById("btnExportarXlsx").addEventListener("click", () => baixarRelatorio("xlsx"));

    carregarSetores();
    carregarRelatorio();
});

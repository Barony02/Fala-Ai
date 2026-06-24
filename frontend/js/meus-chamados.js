const API_URL = window.location.hostname === 'localhost' 
    ? "http://localhost:8000/api"
    : `${window.location.protocol}//${window.location.hostname}:8000/api`;

document.addEventListener("DOMContentLoaded", () => {
    const token = localStorage.getItem("token");
    
    if (!token) {
        window.location.href = "/index.html";
        return;
    }

    const statusFilter = document.getElementById('statusFilter');
    const tbody = document.getElementById('chamadosTableBody');
    
    // Elementos do Modal
    const modal = document.getElementById("chamadoModal");
    const closeButton = document.querySelector(".close-button");
    
    let chamadosLista = []; // Guarda os dados vindos do banco

    async function carregarChamados() {
        const status = statusFilter.value;
        let url = `${API_URL}/meus-chamados`;
        
        if (status) {
            url += `?status=${status}`;
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

            chamadosLista = await response.json();
            tbody.innerHTML = '';

            if (chamadosLista.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: #666;">Nenhum chamado encontrado.</td></tr>`;
                return;
            }

            chamadosLista.forEach(chamado => {
                const tr = document.createElement('tr');
                tr.style.cursor = "pointer"; // Indica que a linha é clicável
                tr.title = "Clique para ver detalhes";
                
                let statusClass = 'status-aberto';
                if (chamado.status === 'Em Progresso') statusClass = 'status-progresso';
                if (chamado.status === 'Fechado') statusClass = 'status-fechado';

                const dataFormatada = chamado.data_criacao 
                    ? new Date(chamado.data_criacao).toLocaleDateString('pt-BR') 
                    : '-';

                tr.innerHTML = `
                    <td>${chamado.id}</td>
                    <td><strong>${chamado.titulo}</strong></td>
                    <td><span class="status-badge ${statusClass}">${chamado.status}</span></td>
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

    function abrirDetalhesModal(id) {
        const chamado = chamadosLista.find(c => c.id === id);
        if (!chamado) return;

        // Injeta os dados no modal
        document.getElementById("modalId").textContent = chamado.id;
        document.getElementById("modalTitulo").textContent = chamado.titulo;
        document.getElementById("modalPrioridade").textContent = chamado.prioridade;
        document.getElementById("modalSetor").textContent = chamado.setor_responsavel;
        document.getElementById("modalResponsavel").textContent = chamado.usuario_responsavel;
        document.getElementById("modalDescricao").textContent = chamado.descricao;
        
        const dataCompleta = chamado.data_criacao 
            ? new Date(chamado.data_criacao).toLocaleString('pt-BR') 
            : '-';
        document.getElementById("modalData").textContent = dataCompleta;

        // Gerencia classes de status no modal
        const statusSpan = document.getElementById("modalStatus");
        statusSpan.textContent = chamado.status;
        statusSpan.className = "status-badge";
        if (chamado.status === 'Aberto') statusSpan.classList.add('status-aberto');
        if (chamado.status === 'Em Progresso') statusSpan.classList.add('status-progresso');
        if (chamado.status === 'Fechado') statusSpan.classList.add('status-fechado');

        // Exibe o modal
        modal.style.display = "block";
    }

    // Fechar modal ao clicar no (X) ou fora dele
    closeButton.addEventListener("click", () => modal.style.display = "none");
    window.addEventListener("click", (event) => {
        if (event.target === modal) modal.style.display = "none";
    });

    statusFilter.addEventListener('change', carregarChamados);
    carregarChamados();
});
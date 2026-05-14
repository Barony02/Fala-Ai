# Projeto: Sistema de Gestão de Chamados Intersetoriais (Câmara de Mariana)

## 1. Descrição Geral
O sistema proposto consiste em uma plataforma de comunicação interna projetada para a **Câmara Municipal de Mariana**, com o objetivo de centralizar, organizar e monitorar a solicitação de serviços e a interação entre os diferentes departamentos da instituição.

### Objetivos do Sistema
*   **Centralização de Demandas:** Substituir métodos informais de comunicação por um fluxo de trabalho estruturado, onde cada solicitação é registrada como um "chamado" (ticket).
*   **Eficiência Intersetorial:** Facilitar o contato direto entre áreas distintas (ex: Informática, Limpeza, Administrativo), permitindo que um setor requisite suporte de outro de forma rápida e documentada.
*   **Transparência e Controle:** Oferecer visibilidade total sobre o status das solicitações, desde a abertura até a conclusão.

### Funcionalidades Principais
*   **Módulo de Solicitação (Usuário):** Interface para a abertura de chamados, onde o solicitante descreve a necessidade, seleciona o setor de destino e define a prioridade.
*   **Painel de Atendimento (Setores):** Visualização das demandas recebidas pelo setor, com opções para atualizar o status (em atendimento, aguardando peça, concluído).
*   **Módulo de Gestão (ADM):** Ferramenta de monitoramento para administradores, permitindo visualizar o tempo de resposta de cada setor e o volume de chamados abertos.
*   **Monitoramento de Produtividade:** Sistema de alertas para chamados que ultrapassarem o tempo limite de atendimento, permitindo que o gestor identifique gargalos e cobre a resolução dos setores responsáveis.

---

## 2. Especificações do Projeto

### Problema e Relação com os ODS
*   **Problema:** A descentralização da comunicação interna na Câmara de Mariana gera atrasos, perda de informações e falta de transparência na execução de tarefas entre setores. A ausência de métricas de tempo de resposta dificulta a gestão da produtividade e a identificação de gargalos operacionais.
*   **Relação com os ODS:** 
    *   **ODS 16 (Paz, Justiça e Instituições Eficazes):** Alinha-se à meta 16.6, que visa desenvolver instituições eficazes, responsáveis e transparentes em todos os níveis, ao auditar processos internos.
    *   **ODS 9 (Indústria, Inovação e Infraestrutura):** Promove a modernização tecnológica da infraestrutura pública local através da inovação digital.

### Público-alvo
*   Servidores e funcionários da Câmara Municipal de Mariana.
*   Chefias de departamentos e setores administrativos.
*   Gestores de TI e Administradores institucionais.

### Tecnologias Previstas
*   **Frontend:** React (Interface web responsiva).
*   **Backend:** PHP (PDO) ou Python para a lógica do servidor.
*   **Banco de Dados:** MySQL ou SQLite para armazenamento de chamados e logs.
*   **Ambiente:** Ambientes baseados em Linux para desenvolvimento e hospedagem.

### Lista de Integrantes
*   Gabriel Barony
*   Gustavo Meira
*   Marco Antônio Diniz
*   Thiago Martins Zanete 
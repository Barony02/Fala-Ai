# Documento de Requisitos e Casos de Uso - Sistema de Comunicação Interna (Câmara de Mariana)

## 1. Perfis de Usuário (Atores)
* **Usuário Solicitante (Funcionário/Técnico):** Perfil base do sistema que engloba os funcionários de todos os setores (incluindo a equipe técnica). Tem a capacidade de abrir chamados, anexar arquivos, acompanhar status, interagir em solicitações, avaliar atendimentos recebidos, reabrir chamados dentro do prazo e responder a chamados que estejam sob sua responsabilidade técnica de atendimento.
* **Gestor do Setor (Administrador Setorial):** Possui controle administrativo restrito ao seu setor. Funciona como um administrador para a sua área: gerencia usuários do seu setor, configura as categorias de serviços que seu setor oferece, monitora a fila de chamados local, atribui e redistribui tarefas, avalia prazos (SLA), visualiza dashboards em tempo real do setor e extrai relatórios gerenciais da sua respectiva secretaria. Também herda todas as funções de abertura e resposta a chamados.
* **Administrador Geral:** Possui visão global, irrestrita e controle total sobre todo o sistema. Gerencia os cadastros de todos os usuários, todos os setores e categorias de serviço de forma global, monitora filas de todas as áreas, avalia prazos (SLA) gerais, visualiza dashboards de toda a instituição e extrai relatórios consolidados de todos os setores. Também herda todas as funções de abertura e resposta a chamados.

---

## 2. Requisitos Funcionais (RF)
* **RF01 - Autenticação e Autorização:** O sistema deve permitir o login seguro de usuários validando o e-mail funcional e a senha cadastrada, controlando o acesso baseado no perfil (Solicitante/Técnico, Gestor do Setor ou Administrador Geral). O acesso deve ser bloqueado temporariamente após 5 tentativas consecutivas incorretas.
* **RF02 - Gerenciamento de Usuários:** O Administrador Geral pode gerenciar todos os usuários do sistema globalmente. O Gestor do Setor pode listar, editar, cadastrar ou inativar os usuários que pertencem estritamente ao seu setor de atuação.
* **RF03 - Gerenciamento de Setores e Categorias:** O Administrador Geral pode gerenciar todos os setores e categorias do sistema. O Gestor do Setor pode cadastrar, editar e configurar as categorias de serviços oferecidas especificamente pelo seu setor de atuação.
* **RF04 - Abertura de Chamados:** Qualquer usuário autenticado (Solicitante/Técnico, Gestor ou Administrador) deve poder criar chamados exigindo obrigatoriamente título, setor de destino, categoria e descrição detalhada do problema. O nível de prioridade inicial pode ser sugerido pelo criador.
* **RF05 - Anexos em Chamados:** O sistema deve permitir o upload opcional de arquivos (imagens nos formatos JPG/PNG ou documentos em PDF) durante a abertura e nas interações do chamado.
* **RF06 - Interação, Resposta e Histórico Cronológico:** O sistema deve manter um chat/histórico cronológico permanente contendo mensagens, notas internas da equipe, mudanças de status, data, horário e o responsável por cada ação. Qualquer usuário atribuído ou com permissão no chamado pode interagir e responder.
* **RF07 - Transferência Intersetorial:** O usuário responsável pelo atendimento, o Gestor do Setor de origem/destino ou o Administrador Geral podem encaminhar um chamado para outro setor caso identifiquem erro no direcionamento, exigindo obrigatoriamente uma justificativa em texto.
* **RF08 - Notificações e Alertas:** O sistema deve emitir alertas automáticos (via e-mail ou notificação interna) para o criador do chamado quando houver atualizações, e para o setor de destino quando um novo chamado for aberto, reaberto ou transferido.
* **RF09 - Busca e Filtros Avançados:** O sistema deve disponibilizar uma ferramenta de busca por número do chamado e filtros avançados (por status, intervalo de datas, setor solicitante, setor atendente e prioridade), respeitando as regras de visibilidade de cada perfil.
* **RF10 - Avaliação de Atendimento:** Assim que o chamado for marcado como concluído, o usuário que realizou a abertura deve poder avaliar o serviço prestado por meio de uma escala de 1 a 5 estrelas.
* **RF11 - Dashboard de Monitoramento:** O sistema deve exibir painéis de métricas em tempo real (chamados abertos, em atraso e concluídos). O Gestor do Setor visualiza os dados e métricas em tempo real apenas da sua respectiva área. O Administrador Geral possui uma visão de painel global do sistema.
* **RF12 - Relatórios Gerenciais:** O Administrador Geral deve poder exportar relatórios consolidados nos formatos PDF e Excel de todos os setores. O Gestor do Setor pode exportar relatórios detalhados específicos de sua área de atuação. Ambos os relatórios devem calcular o tempo médio de resposta (SLA) e notas de avaliação.

---

## 3. Requisitos Não Funcionais (RNF)
* **RNF01 - Usabilidade e Responsividade:** A interface do sistema deve ser responsiva, garantindo a usabilidade tanto em computadores desktop quanto em dispositivos móveis.
* **RNF02 - Segurança (Criptografia):** As senhas dos usuários devem ser armazenadas no banco de dados utilizando algoritmos de hash seguros (ex: BCrypt).
* **RNF03 - Desempenho:** O sistema deve carregar as listagens de chamados, filtros e dashboards em menos de 3 segundos.
* **RNF04 - Auditoria (Logs do Sistema):** O sistema deve registrar em log dados críticos e irreversíveis (como exclusão/inativação de usuários, alterações de perfis ou reajustes históricos), garantindo a rastreabilidade de quem realizou a ação.
* **RNF05 - Disponibilidade:** O sistema deve ser projetado para operar com alta disponibilidade durante o horário comercial da Câmara Municipal.

---

## 4. Regras de Negócio (RN)
* **RN01 - Controle de Fechamento:** Um chamado só pode ser alterado para o status "Concluído" pelo usuário especificamente atribuído/responsável pelo atendimento, pelo Gestor do Setor de destino ou pelo Administrador Geral.
* **RN02 - Acordo de Nível de Serviço (SLA) e Cronometragem:** O sistema iniciará uma cronometragem automática no momento exato da criação do chamado. Cada prioridade (Baixa, Média, Alta, Urgente) possuirá um prazo máximo de resolução em horas úteis. O tempo total acumulado em cada status deve ser gravado.
* **RN03 - Alertas Visuais de SLA:** O sistema deve exibir sinalizações visuais coloridas baseadas no tempo limite do chamado: amarelo para prazos críticos e vermelho para prazos estourados.
* **RN04 - Reajuste de Prioridade:** O usuário responsável pelo atendimento, o Gestor do Setor ou o Administrador Geral podem alterar a prioridade de um chamado, sendo obrigados a inserir uma justificativa que constará no histórico.
* **RN05 - Reabertura de Chamado:** O usuário que abriu o chamado pode reabri-lo caso o problema persista, desde que o faça no prazo limite de até **48 horas úteis** após o fechamento. Após este prazo, o chamado é bloqueado definitivamente. A reabertura altera o status para "Aberto" e notifica os responsáveis pelo setor de destino.
* **RN06 - Visibilidade Restrita e Hierárquica:** 
    * O **Usuário Solicitante (Funcionário/Técnico)** visualiza apenas os chamados abertos por ele mesmo, pelo seu próprio setor, ou chamados de outros setores que tenham sido atribuídos a ele para atendimento.
    * O **Gestor do Setor** visualiza todos os chamados abertos pelo seu setor, todos os chamados direcionados/atribuídos ao seu setor de atuação e possui autonomia administrativa para visualizar e gerenciar usuários e categorias exclusivamente de sua área.
    * O **Administrador Geral** possui visão irrestrita de todas as áreas, usuários, configurações e chamados do sistema.

---

## 5. Mapeamento de Casos de Uso (Estrutura do Diagrama)

Para corrigir a arquitetura do diagrama de casos de uso, as relações devem seguir a seguinte estrutura lógica:

* **Solicitante/Técnico (Ator Base):** Abre chamados, responde e interage em chamados sob sua responsabilidade, anexa arquivos, avalia atendimentos e reabre chamados.
* **Gestor do Setor (Ator Especializado):** Herda todas as funcionalidades do Solicitante/Técnico. Adicionalmente, possui permissões administrativas limitadas ao seu setor, como: gerenciar usuários do setor, gerenciar categorias de serviço do setor, monitorar e distribuir a fila de demandas da área e extrair relatórios locais.
* **Administrador Geral (Ator Especializado):** Herda todas as funcionalidades do Solicitante/Técnico. Adicionalmente, gerencia cadastros globais (todos os usuários, setores, categorias), possui visão total de relatórios/dashboards institucionais e controle irrestrito do sistema.

---

## 6. Diagrama de Casos de Uso
![Diagrama de Casos de Uso](images/diagrama%20eng2.png)
*Nota: O diagrama acima representa os atores (Solicitante/Técnico, Gestor do Setor, Administrador Geral) e suas interações com as funcionalidades do sistema.*

# Histórias de Usuário

### US01: Autenticação de Usuários
* **Descrição:** Como **Usuário autenticado (Solicitante/Técnico, Gestor ou Administrador)**, quero realizar login no sistema informando minhas credenciais para acessar as funcionalidades e telas associadas ao meu perfil de acesso.
* **Critérios de Aceitação:**
    * O sistema deve validar o acesso através de e-mail funcional e senha cadastrados.
    * O sistema deve direcionar o usuário para a interface correspondente ao seu nível de permissão (Solicitante/Técnico, Gestor do Setor ou Administrador Geral).
    * O acesso deve ser temporariamente bloqueado após 5 tentativas consecutivas de login incorretas para prevenir acessos não autorizados.

---

### US02: Abertura de Chamado por Qualquer Perfil
* **Descrição:** Como **Usuário do Sistema**, quero registrar uma nova solicitação detalhando o problema para que o setor competente possa iniciar o atendimento.
* **Critérios de Aceitação:**
    * Qualquer perfil (Solicitante/Técnico, Gestor ou Administrador) deve ter acesso à tela de abertura de chamados.
    * O formulário de abertura deve exigir obrigatoriamente preenchimento de título, descrição clara do problema, seleção da categoria e seleção do setor de destino.
    * O sistema deve permitir o upload opcional de um arquivo anexo nos formatos de imagem (JPG/PNG) ou documento (PDF).
    * Após o envio, o sistema deve emitir um alerta automático para o setor de destino informando sobre o novo chamado.

---

### US03: Gestão de Atendimento e Respostas
* **Descrição:** Como **Usuário Atribuído**, quero responder ao chamado e gerenciar seu progresso para dar andamento e solucionar a demanda recebida.
* **Critérios de Aceitação:**
    * O usuário designado para o suporte (Técnico, Gestor do Setor ou Administrador) deve visualizar o chamado em sua fila de trabalho.
    * O sistema deve permitir a alteração manual do status do chamado entre as opções válidas: "Em Atendimento", "Pausado" ou "Concluído".
    * A alteração para o status "Concluído" só pode ser realizada pelo responsável técnico do atendimento, pelo Gestor do Setor destinatário ou pelo Administrador Geral.
    * As respostas e notas de progresso inseridas devem ser registradas e exibidas de forma clara no histórico cronológico do chamado.

---

### US04: Redirecionamento Intersetorial
* **Descrição:** Como **Gestor do Setor**, **Administrador Geral** ou **Técnico Responsável**, quero encaminhar um chamado recebido para outro setor da Câmara caso identifique que a responsabilidade da resolução pertence a outra área.
* **Critérios de Aceitação:**
    * O sistema deve exigir uma justificativa em texto para validar a transferência de setor.
    * O chamado transferido deve sair da fila do setor de origem e aparecer imediatamente na listagem do setor de destino.
    * O histórico do chamado deve registrar permanentemente quem realizou a transferência, a data, o horário e o motivo da ação.

---

### US05: Avaliação e Encerramento de Chamado
* **Descrição:** Como **Criador do Chamado**, quero avaliar o suporte recebido após a conclusão da solicitação e ter a opção de reabrir o caso se o problema persistir.
* **Critérios de Aceitação:**
    * O sistema deve disponibilizar um módulo de avaliação por notas (escala de 1 a 5 estrelas) assim que o chamado for marcado como concluído.
    * Caso a solução enviada não tenha resolvido o problema, o criador do chamado deve ter um botão visível para "Reabrir Chamado" ativo pelo prazo limite estrito de **48 horas úteis** após o fechamento.
    * Após o prazo de 48 horas úteis, o chamado deve ser bloqueado definitivamente para reaberturas.
    * A ação de reabertura deve retornar o status do chamado para "Aberto" e alertar a equipe técnica do setor responsável.

---

### US06: Gestão e Configuração Administrativa Local do Setor
* **Descrição:** Como **Gestor do Setor**, quero poder gerenciar os usuários e as categorias de serviço da minha secretaria de forma autônoma para manter o fluxo do setor organizado sem depender do Administrador Geral.
* **Critérios de Aceitação:**
    * O Gestor deve conseguir visualizar, cadastrar, editar e inativar apenas os usuários que estejam vinculados ao seu próprio setor.
    * O Gestor deve conseguir cadastrar, editar e desativar as categorias de serviço oferecidas exclusivamente pelo seu setor.
    * Tentativas de alteração de usuários ou categorias de outros setores por parte do Gestor devem ser bloqueadas pelo sistema.

---

### US07: Monitoramento de SLA, Dashboards e Relatórios
* **Descrição:** Como **Gestor do Setor** ou **Administrador Geral**, quero monitorar os prazos através de alertas visuais, visualizar painéis métricos e exportar relatórios para auditar os resultados.
* **Critérios de Aceitação:**
    * O sistema deve realizar a cronometragem baseada no SLA cadastrado para a prioridade e exibir alertas visuais (amarelo para crítico, vermelho para estourado).
    * O Gestor do Setor deve ter acesso ao painel de monitoramento e exportação de relatórios (PDF/Excel) restritos aos dados de sua secretaria.
    * O Administrador Geral possui acesso irrestrito aos dashboards consolidados e relatórios de todas as secretarias e setores da Câmara.
    * A alteração de prioridade de um chamado por parte do Gestor do Setor ou Administrador Geral exige obrigatoriamente o preenchimento de justificativa em texto para o histórico.
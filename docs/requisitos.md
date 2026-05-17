# Documento de Requisitos e Casos de Uso - Sistema de Comunicação Interna (Câmara de Mariana)

## 1. Perfis de Usuário (Atores)
* **Usuário Solicitante (Antigo Usuário Padrão/Comum):** Funcionários dos diversos setores da Câmara. Podem abrir chamados, anexar arquivos, acompanhar o status, interagir nas solicitações criadas, avaliar o atendimento recebido e reabrir chamados dentro do prazo regulamentar.
* **Técnico de Atendimento (Antigo Atendente/Setor Destino):** Funcionários dos setores que prestam suporte (ex: Informática, Manutenção). Podem assumir, gerenciar e transferir chamados de sua área, atualizar o status e registrar ações no histórico.
* **Gestor Administrador (Antigo Chefe/Gestor):** Possui visão global e irrestrita do sistema. Gerencia os cadastros de usuários, setores e categorias de serviço, monitora filas, avalia prazos (SLA), identifica gargalos, visualiza dashboards em tempo real e extrai relatórios gerenciais.

---

## 2. Requisitos Funcionais (RF)
* **RF01 - Autenticação e Autorização:** O sistema deve permitir o login seguro de usuários validando o e-mail funcional e a senha cadastrada, controlando o acesso baseado no perfil (Solicitante, Técnico ou Gestor). O acesso deve ser bloqueado temporariamente após 5 tentativas consecutivas incorretas.
* **RF02 - Gerenciamento de Usuários:** O Gestor Administrador deve poder cadastrar, editar, inativar e listar os usuários do sistema, vinculando-os a seus respectivos setores.
* **RF03 - Gerenciamento de Setores e Categorias:** O Gestor Administrador deve poder cadastrar e configurar os setores da Câmara e as respectivas categorias de serviços que cada setor oferece.
* **RF04 - Abertura de Chamados:** O Usuário Solicitante deve poder criar chamados exigindo obrigatoriamente título, setor de destino, categoria e descrição detalhada do problema. O nível de prioridade inicial pode ser sugerido pelo solicitante.
* **RF05 - Anexos em Chamados:** O sistema deve permitir o upload opcional de arquivos (imagens nos formatos JPG/PNG ou documentos em PDF) durante a abertura e nas interações do chamado.
* **RF06 - Interação e Histórico Cronológico:** O sistema deve manter um chat/histórico cronológico permanente contendo mensagens, notas internas da equipe técnica, mudanças de status, data, horário e o responsável por cada ação.
* **RF07 - Transferência Intersetorial:** O Técnico de Atendimento ou o Gestor Administrador podem encaminhar um chamado para outro setor caso identifiquem erro no direcionamento, exigindo obrigatoriamente uma justificativa em texto.
* **RF08 - Notificações e Alertas:** O sistema deve emitir alertas automáticos (via e-mail ou notificação interna) para o solicitante quando houver atualizações, e para o setor de destino quando um novo chamado for aberto ou reaberto.
* **RF09 - Busca e Filtros Avançados:** O sistema deve disponibilizar uma ferramenta de busca por número do chamado e filtros avançados (por status, intervalo de datas, setor solicitante, setor atendente e prioridade).
* **RF10 - Avaliação de Atendimento:** Assim que o chamado for marcado como concluído, o Usuário Solicitante deve poder avaliar o serviço prestado por meio de uma escala de 1 a 5 estrelas.
* **RF11 - Dashboard de Monitoramento:** O sistema deve exibir para o Gestor Administrador um painel com métricas em tempo real (chamados abertos, em atraso e concluídos na semana).
* **RF12 - Relatórios Gerenciais:** O Gestor Administrador deve poder exportar relatórios consolidados nos formatos PDF e Excel, aplicando filtros por período (mês/ano) e setores, exibindo o tempo médio de resposta (SLA) e notas de avaliação.

---

## 3. Requisitos Não Funcionais (RNF)
* **RNF01 - Usabilidade e Responsividade:** A interface do sistema deve ser responsiva, garantindo a usabilidade tanto em computadores desktop quanto em dispositivos móveis.
* **RNF02 - Segurança (Criptografia):** As senhas dos usuários devem ser armazenadas no banco de dados utilizando algoritmos de hash seguros (ex: BCrypt).
* **RNF03 - Desempenho:** O sistema deve carregar as listagens de chamados, filtros e dashboards em menos de 3 segundos.
* **RNF04 - Auditoria (Logs do Sistema):** O sistema deve registrar em log dados críticos e irreversíveis (como exclusão/inativação de usuários ou reajustes históricos), garantindo a rastreabilidade de quem realizou a ação.
* **RNF05 - Disponibilidade:** O sistema deve ser projetado para operar com alta disponibilidade durante o horário comercial da Câmara Municipal.

---

## 4. Regras de Negócio (RN)
* **RN01 - Controle de Fechamento:** Um chamado só pode ser alterado para o status "Concluído" pelo Técnico de Atendimento explicitamente atribuído/responsável pelo chamado ou pelo Gestor Administrador.
* **RN02 - Acordo de Nível de Serviço (SLA) e Cronometragem:** O sistema iniciará uma cronometragem automática no momento exato da criação do chamado. Cada prioridade (Baixa, Média, Alta, Urgente) possuirá um prazo máximo de resolução em horas úteis. O tempo total acumulado em cada status deve ser gravado.
* **RN03 - Alertas Visuais de SLA:** O sistema deve exibir sinalizações visuais coloridas baseadas no tempo limite do chamado: amarelo para prazos críticos e vermelho para prazos estourados.
* **RN04 - Reajuste de Prioridade:** O Técnico de Atendimento ou o Gestor Administrador podem alterar a prioridade de um chamado, mas são obrigados a inserir uma justificativa que constará no histórico.
* **RN05 - Reabertura de Chamado:** O Usuário Solicitante pode reabrir um chamado caso o problema persista, desde que o faça no prazo limite de até **48 horas úteis** após o fechamento. Após este prazo, o chamado é bloqueado definitivamente. A reabertura altera o status para "Aberto" e notifica o técnico.
* **RN06 - Visibilidade Restrita e Setorial:** O Usuário Solicitante só pode visualizar chamados abertos por ele mesmo ou pelo seu próprio setor. O Técnico de Atendimento visualiza apenas os chamados atribuídos ao seu respectivo setor. Apenas o Gestor Administrador possui visão irrestrita de todas as áreas e chamados.

---

## 5. Mapeamento de Casos de Uso (Estrutura do Diagrama)

Para corrigir a arquitetura do diagrama de casos de uso, as relações devem seguir a seguinte estrutura lógica:

## 6. Diagrama de Casos de Uso
![Diagrama de Casos de Uso](images/Diagrama%20de%20casos%20de%20uso.png)
*Nota: O diagrama acima representa os atores (Servidor, Técnico, Administrador) e suas interações com as funcionalidades do sistema.*

# Histórias de Usuário

### US01: Autenticação de Servidores
* **Descrição:** Como **Usuário Solicitante**, **Técnico de Atendimento** ou **Gestor Administrador**, quero realizar login no sistema informando minhas credenciais para acessar as funcionalidades e telas associadas ao meu perfil de acesso.
* **Critérios de Aceitação:**
    * O sistema deve validar o acesso através de e-mail funcional e senha cadastrados.
    * O sistema deve direcionar o usuário para a interface correspondente ao seu nível de permissão: "Usuário Solicitante", "Técnico de Atendimento" ou "Gestor Administrador".
    * O acesso deve ser temporariamente bloqueado após 5 tentativas consecutivas de login incorretas para prevenir acessos não autorizados.

---

### US02: Abertura de Chamado
* **Descrição:** Como **Usuário Solicitante**, quero registrar uma nova solicitação detalhando o problema para que o setor competente possa iniciar o atendimento.
* **Critérios de Aceitação:**
    * O formulário de abertura deve exigir obrigatoriamente preenchimento de título, descrição clara do problema, seleção da categoria e seleção do setor de destino.
    * O sistema deve permitir o upload opcional de um arquivo anexo nos formatos de imagem (JPG/PNG) ou documento (PDF).
    * Após o envio, uma mensagem clara de sucesso ou falha deve ser exibida na tela por meio de uma notificação temporária.
    * O sistema deve emitir um alerta automático para o setor de destino assim que o chamado for criado.

---

### US03: Gestão de Atendimento pelo Setor
* **Descrição:** Como **Técnico de Atendimento**, quero gerenciar a fila de chamados recebidos para atualizar o andamento das demandas da minha área.
* **Critérios de Aceitação:**
    * O técnico deve visualizar apenas a lista de chamados atribuídos ao seu respectivo setor de atuação.
    * O sistema deve permitir a alteração manual do status do chamado entre as opções válidas: "Em Atendimento", "Pausado" ou "Concluído".
    * A alteração para o status "Concluído" só pode ser realizada pelo técnico explicitamente responsável pelo chamado ou pelo Gestor Administrador.
    * O técnico deve conseguir inserir notas de progresso que fiquem salvas no histórico cronológico do chamado.

---

### US04: Redirecionamento Intersetorial
* **Descrição:** Como **Técnico de Atendimento** ou **Gestor Administrador**, quero encaminhar um chamado recebido para outro setor da Câmara caso identifique que a responsabilidade da resolução pertence a outra área.
* **Critérios de Aceitação:**
    * O sistema deve exigir uma justificativa em texto para validar a transferência de setor.
    * O chamado transferido deve sair da fila do setor atual e aparecer imediatamente na listagem do setor de destino.
    * O histórico do chamado deve registrar permanentemente quem realizou a transferência, a data, o horário e o motivo da ação.

---

### US05: Avaliação e Encerramento pelo Usuário
* **Descrição:** Como **Usuário Solicitante**, quero avaliar o suporte recebido após a conclusão do chamado e ter a opção de reabrir o caso se o problema persistir.
* **Critérios de Aceitação:**
    * O sistema deve disponibilizar um módulo de avaliação por notas (escala de 1 a 5 estrelas) assim que o chamado for marcado como concluído.
    * Caso a solução enviada não tenha resolvido o problema, o usuário deve ter um botão visível para "Reabrir Chamado" ativo pelo prazo limite estrito de **48 horas úteis** após o fechamento.
    * Após o prazo de 48 horas úteis, o chamado deve ser bloqueado definitivamente para reaberturas.
    * A ação de reabertura deve retornar o status do chamado para "Aberto" e alertar o técnico responsável.

---

### US06: Monitoramento de SLA e Prazos
* **Descrição:** Como **Gestor Administrador**, quero que o sistema monitore automaticamente o tempo de atendimento de cada chamado para evitar atrasos nas demandas institucionais.
* **Critérios de Aceitação:**
    * O sistema deve iniciar uma cronometragem automática no momento exato em que o chamado for criado.
    * Devem ser emitidos alertas visuais com cores distintas (amarelo para prazo crítico e vermelho para chamado com prazo estourado) baseados no tempo limite em horas úteis cadastrado para a prioridade daquela solicitação.
    * Caso o Técnico de Atendimento ou o Gestor Administrador alterem a prioridade do chamado, o sistema deve exigir obrigatoriamente uma justificativa para o histórico.
    * O tempo total acumulado em cada status deve ser gravado para composição de métricas futuras.

---

### US07: Extração de Relatórios Gerenciais
* **Descrição:** Como **Gestor Administrador**, quero gerar relatórios consolidados sobre os atendimentos realizados para auditar a eficiência das secretarias.
* **Critérios de Aceitação:**
    * O sistema deve permitir a aplicação de filtros avançados por intervalo de datas (mês/ano) e por setores específicos.
    * O arquivo gerado deve calcular e exibir o tempo médio de resposta (SLA) de cada setor e as notas de avaliação automaticamente.
    * A exportação dos dados consolidados deve ser disponibilizada nativamente nos formatos PDF e Excel.
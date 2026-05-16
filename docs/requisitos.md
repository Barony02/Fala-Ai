# Documento de Requisitos - Sistema de Comunicação Interna (Câmara de Mariana)

## 1. Perfis de Usuário (Atores)
* **Usuário Padrão (Solicitante):** Funcionários dos diversos setores. Podem abrir chamados, anexar arquivos, acompanhar o status, interagir nas solicitações criadas e avaliar o atendimento recebido.
* **Atendente (Setor Solicitado):** Funcionários dos setores que prestam suporte (ex: Informática, Manutenção). Podem assumir chamados, atualizar o status, registrar ações, transferir chamados e finalizar solicitações.
* **Gestor (Administrador):** Possui visão global. Gerencia os cadastros do sistema, monitora filas de chamados, avalia prazos (SLA), identifica gargalos e extrai relatórios de produtividade.

## 2. Requisitos Funcionais (RF)
* **RF01 - Autenticação e Autorização:** O sistema deve permitir o login seguro de usuários e controlar o acesso baseado no perfil (Padrão, Atendente, Gestor).
* **RF02 - Gerenciamento de Usuários:** O Gestor deve poder cadastrar, editar, inativar e listar os usuários do sistema, vinculando-os a seus respectivos setores.
* **RF03 - Gerenciamento de Setores e Categorias:** O sistema deve permitir o cadastro dos setores da Câmara e as categorias de serviços que cada setor oferece.
* **RF04 - Abertura de Chamados:** O sistema deve permitir a criação de chamados com título, setor de destino, categoria, descrição detalhada e nível de prioridade sugerido.
* **RF05 - Anexos em Chamados:** O sistema deve permitir o upload de arquivos (imagens, PDFs, documentos) durante a abertura e nas interações do chamado.
* **RF06 - Interação e Acompanhamento:** O sistema deve manter um chat/histórico cronológico de mensagens e mudanças de status dentro de cada chamado.
* **RF07 - Transferência de Chamados:** O sistema deve permitir que um setor atendente encaminhe um chamado para outro setor, caso a demanda tenha sido direcionada incorretamente.
* **RF08 - Notificações:** O sistema deve emitir alertas (via e-mail ou notificação interna) para o criador quando houver atualização no chamado, e para o setor quando um novo chamado for aberto.
* **RF09 - Busca e Filtros:** O sistema deve disponibilizar uma busca por número do chamado e filtros avançados (por status, data, setor solicitante, setor atendente e prioridade).
* **RF10 - Avaliação de Atendimento:** Após o fechamento do chamado, o usuário solicitante deve poder avaliar o serviço prestado (ex: nota de 1 a 5).
* **RF11 - Dashboard de Monitoramento:** O sistema deve exibir para o Gestor um painel com métricas em tempo real (chamados abertos, chamados em atraso, chamados concluídos na semana).
* **RF12 - Relatórios Gerenciais:** O Gestor deve poder exportar relatórios (PDF/Excel) com estatísticas de produtividade por setor, tempo médio de resposta e notas de avaliação.

## 3. Requisitos Não Funcionais (RNF)
* **RNF01 - Usabilidade e Responsividade:** A interface deve ser responsiva, permitindo o uso adequado tanto em computadores *desktop* quanto em dispositivos móveis.
* **RNF02 - Segurança (Senhas):** As senhas dos usuários devem ser armazenadas no banco de dados utilizando algoritmos de *hash* (ex: BCrypt).
* **RNF03 - Desempenho:** O sistema deve carregar as listagens de chamados e dashboards em menos de 3 segundos para não prejudicar a agilidade do fluxo de trabalho.
* **RNF04 - Auditoria (Logs):** O sistema deve registrar em *log* dados críticos, como quem excluiu um usuário ou quem alterou o status de um chamado finalizado, garantindo a rastreabilidade.
* **RNF05 - Disponibilidade:** O sistema deve ser projetado para operar com alta disponibilidade durante o horário comercial da Câmara Municipal.

## 4. Regras de Negócio (RN)
* **RN01 - Fechamento de Chamado:** Um chamado só pode ser dado como "Concluído" pelo Atendente responsável ou pelo Gestor.
* **RN02 - Acordo de Nível de Serviço (SLA):** Cada prioridade definida na abertura (Baixa, Média, Alta, Urgente) deve ter um prazo máximo de resolução predefinido em horas úteis.
* **RN03 - Reajuste de Prioridade:** O Atendente ou o Gestor podem alterar a prioridade de um chamado, mas devem obrigatoriamente inserir uma justificativa no histórico.
* **RN04 - Reabertura de Chamado:** O usuário solicitante tem até 48 horas úteis após o fechamento para reabrir o chamado, caso o problema persista. Após esse prazo, o chamado é bloqueado definitivamente.
* **RN05 - Visibilidade Setorial:** Usuários Padrão só podem visualizar os chamados abertos por eles mesmos ou pelo seu próprio setor. Apenas Gestores têm visão irrestrita de todas as áreas.
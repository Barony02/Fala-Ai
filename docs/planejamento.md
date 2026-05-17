# Planejamento de Sprints

Este documento apresenta o cronograma macro para o desenvolvimento do sistema de gestão de chamados da Câmara de Mariana, estruturado em sprints focadas em entregas incrementais e funcionais.

📌 **Quadro Kanban:**  
https://github.com/users/Barony02/projects/6/views/1

---

## Sprint 1


### Objetivos Principais
- Configurar o ambiente de desenvolvimento local unificado da equipe.
- Modelar o banco de dados e cadastrar as entidades estruturais (como os setores da Câmara).
- Implementar o sistema de autenticação segura e controle de níveis de acesso.
- Desenvolver a camada de serviços back-end para expor os primeiros endpoints do sistema.
- Documentar a arquitetura técnica inicial.

### Tarefas
1. Configurar o ambiente de desenvolvimento local.
2. Desenhar a modelagem do banco de dados e estabelecer a interface de conexão com o sistema.
3. Desenvolver o módulo de autenticação (Login).
4. Implementar o controle de níveis de acesso.
5. Cadastrar a estrutura de setores da Câmara Municipal no banco de dados.
6. Desenvolver os endpoints da API REST.
7. Elaborar a documentação técnica inicial do código.

---

## Sprint 2

### Objetivos Principais
- Desenvolver a identidade visual, menus e estrutura de navegação do front-end.
- Criar a interface de formulário para abertura de chamados.
- Implementar componentes de feedback em tempo real (notificações e carregamento).

---

## Sprint 3

### Objetivos Principais
- Construir o painel operacional (Dashboard).
- Implementar paginação para listagem de dados.
- Desenvolver a máquina de estados dos chamados.
- Criar o sistema de redirecionamento intersetorial.

---

## Sprint 4

### Objetivos Principais
- Desenvolver controle de tempo de resposta (SLA).
- Implementar notas internas e histórico.
- Criar regras de reabertura de chamados.
- Implementar avaliação por estrelas.
- Adicionar modo escuro.

---

## Sprint 5

### Objetivos Principais
- Gerar relatórios gerenciais (PDF/Excel).
- Realizar testes de carga e estresse.
- Aplicar melhorias de segurança.
- Configurar backups automáticos.
- Auditar conformidade (ODS 16).
- Realizar deploy em produção.
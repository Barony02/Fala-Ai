# Sistema de Comunicação Interna – Câmara de Mariana

## Ideia Geral do Projeto

Este projeto tem como objetivo desenvolver um sistema de comunicação interna para a Câmara Municipal de Mariana. A proposta é facilitar a interação entre diferentes setores da instituição por meio da abertura e acompanhamento de chamados, promovendo maior organização, agilidade e transparência nos processos internos.

---

## Descrição Geral do Sistema

O sistema funcionará como uma plataforma centralizada onde setores da Câmara poderão:

- Criar chamados para solicitar serviços de outros setores (ex: informática, limpeza, manutenção, etc.);
- Acompanhar o status dos chamados em tempo real;
- Registrar histórico de interações e atualizações;
- Priorizar demandas conforme necessidade.

Além disso, o sistema contará com um perfil de **gestor (administrador)**, responsável por:

- Monitorar todos os chamados abertos;
- Identificar gargalos e atrasos no atendimento;
- Avaliar produtividade dos setores;
- Cobrar e gerenciar prazos de resolução.

O foco é melhorar a eficiência da comunicação interna e permitir uma gestão mais estratégica das demandas.

---

## Integrantes da Equipe

- Gustavo Meira  
- Marco Antônio Diniz  
- Thiago Martins Zanete  
- Gabriel Barony  

---
## Quadro Kanban

https://github.com/users/Barony02/projects/6/views/1

---

## Execução local

A aplicação foi organizada para rodar localmente como um monolito: o backend FastAPI serve a API e também os arquivos do frontend.

```bash
make build
```

Depois acesse:

```text
http://localhost:8000
```

Credenciais de Acesso
```text
email: admin@admin
senha: 123
```

Comandos úteis:

```bash
make logs      # acompanhar logs
make tests     # rodar testes automatizados no container
make load-test # teste simples de carga local com a aplicação rodando
make backup    # gerar dump SQL local em ./backups
make down      # parar os serviços
make reset     # recriar banco e containers do zero
```

Para agendar backup diário local às 18h:

```bash
bash scripts/install_backup_cron.sh
```

A documentação do backend se encontra em:
```text
http://localhost:8000/docs
```
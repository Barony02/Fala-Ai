# Documentação Técnica Inicial

## Arquitetura Local

O Fala Aí roda localmente como um monolito FastAPI:

- `backend/main.py` inicializa a API, cria/ajusta o schema do banco e serve os arquivos estáticos do frontend.
- `frontend/` contém as telas HTML, CSS e JavaScript servidas pela própria aplicação em `http://localhost:8000`.
- `docker-compose.yml` sobe MySQL e backend. O frontend não precisa de Nginx separado.

## Módulos Principais

- Autenticação e autorização: `backend/app/controllers/auth.py`
- Chamados, SLA, anexos, avaliação e reabertura: `backend/app/controllers/chamado.py`
- Rotas gerais: `backend/app/routes/routes.py`
- Rotas específicas de chamados: `backend/app/routes/chamados.py`
- Modelos SQLAlchemy: `backend/app/models/models.py`
- Schemas Pydantic: `backend/app/schemas/schemas.py`

## Dados e Arquivos

- Banco: MySQL, database `camara_chamados`
- Uploads: `backend/uploads`
- Backups locais: `backups/*.sql`, gerados por `make backup`

## Validação

```bash
make tests
make load-test
```

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import router

# Cria as tabelas do banco de dados automaticamente se não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Chamados - Câmara de Mariana")

# Configuração do CORS necessária para o Frontend (Porta 8080) conversar com o Backend (Porta 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    # reload alterado para False para funcionar estavelmente dentro do contêiner Docker
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
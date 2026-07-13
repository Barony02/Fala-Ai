from pathlib import Path
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.config.database import engine, Base
from app.config import UPLOAD_DIR
from app.routes.routes import router
from app.routes.chamados import router as chamados_router
from sqlalchemy import inspect, text


def ajustar_schema_legado():
    with engine.begin() as conn:
        inspetor = inspect(conn)
        tabelas = set(inspetor.get_table_names())

        if "chamados" in tabelas:
            colunas_chamados = {c["name"] for c in inspetor.get_columns("chamados")}
            if engine.dialect.name == "mysql":
                conn.execute(text("ALTER TABLE chamados MODIFY status VARCHAR(30) NOT NULL DEFAULT 'Aberto'"))
            novas_colunas = {
                "data_fechamento": "DATETIME NULL",
                "avaliacao_nota": "INTEGER NULL",
                "avaliacao_comentario": "VARCHAR(1000) NULL",
                "data_avaliacao": "DATETIME NULL",
            }
            for nome_coluna, definicao in novas_colunas.items():
                if nome_coluna not in colunas_chamados:
                    conn.execute(text(f"ALTER TABLE chamados ADD COLUMN {nome_coluna} {definicao}"))

        if "historico_chamados" in tabelas and engine.dialect.name == "mysql":
            conn.execute(text("ALTER TABLE historico_chamados MODIFY tipo VARCHAR(30) NOT NULL"))

def inicializar_banco_com_retry():
    ultimo_erro = None
    for _ in range(30):
        try:
            Base.metadata.create_all(bind=engine)
            ajustar_schema_legado()
            return
        except Exception as exc:
            ultimo_erro = exc
            time.sleep(2)
    raise ultimo_erro


def garantir_admin_local():
    from bcrypt import gensalt, hashpw
    from app.config.database import SessionLocal
    from app.models.models import Setor, Usuario

    email_admin = "admin@admin"
    senha_admin = "123"
    db = SessionLocal()
    try:
        setor = db.query(Setor).filter(Setor.sigla == "ADM").first()
        if setor is None:
            setor = db.query(Setor).filter(Setor.nome == "Administracao").first()
        if setor is None:
            setor = Setor(nome="Administracao", sigla="ADM")
            db.add(setor)
            db.flush()

        senha_hash = hashpw(senha_admin.encode("utf-8"), gensalt()).decode("utf-8")
        usuario = db.query(Usuario).filter(Usuario.email == email_admin).first()
        if usuario is None:
            usuario = Usuario(
                nome="Administrador Local",
                email=email_admin,
                senha_hash=senha_hash,
                perfil="Administrador",
                setor_id=setor.id,
                ativo=True,
                tentativas_login=0,
                bloqueado_ate=None,
            )
            db.add(usuario)
        else:
            usuario.nome = usuario.nome or "Administrador Local"
            usuario.senha_hash = senha_hash
            usuario.perfil = "Administrador"
            usuario.setor_id = setor.id
            usuario.ativo = True
            usuario.tentativas_login = 0
            usuario.bloqueado_ate = None
        db.commit()
    finally:
        db.close()


inicializar_banco_com_retry()
garantir_admin_local()

app = FastAPI(title="Sistema de Chamados - Câmara de Mariana")

# CORS mantido aberto para facilitar testes locais com navegador e arquivos estáticos do FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def adicionar_headers_seguranca(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.include_router(router, prefix="/api")
app.include_router(chamados_router, prefix="/api")

ROOT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT_DIR / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR / "app"), name="app")
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
    app.mount("/components", StaticFiles(directory=FRONTEND_DIR / "components"), name="components")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def servir_login():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/index.html")
def servir_index():
    return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    # reload alterado para False para funcionar estavelmente dentro do contêiner Docker
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)

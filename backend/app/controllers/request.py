from app.models.models import Usuario, Setor, Chamado, Anexo
from app.schemas.schemas import PedidoSchema
import datetime
from datetime import timezone

def abrirChamado(usuario: Usuario, Pedido: PedidoSchema, db):
    novo_chamado = Chamado(
        titulo=Pedido.titulo,
        descricao=Pedido.descricao,
        setor_solicitante_id=Pedido.setor_solicitante_id,
        setor_responsavel_id=Pedido.setor_responsavel_id,
        prioridade=Pedido.prioridade,
        
        # Preencha ambas as colunas cobradas pelo banco de dados:
        usuario_solicitante_id=usuario.id,  
        usuario_id=usuario.id,  
        
        status="Aberto",
        data_criacao=datetime.datetime.now(timezone.utc),
        data_atualizacao=datetime.datetime.now(timezone.utc)
    )
    db.add(novo_chamado)
    db.commit()
    db.refresh(novo_chamado)
    return {"mensagem": "Chamado aberto com sucesso", "id": novo_chamado.id}
    

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/mensagens", tags=["Mensagens"])

@router.post("/")
def enviar_mensagem(conversa_id: int, remetente_id: int, texto: str, db: Session = Depends(get_db)):
    mensagem = models.Mensagem(conversa_id=conversa_id, remetente_id=remetente_id, texto=texto)
    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)
    return mensagem

@router.get("/")
def listar_mensagens(db: Session = Depends(get_db)):
    return db.query(models.Mensagem).all()
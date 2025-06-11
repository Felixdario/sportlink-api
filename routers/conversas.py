from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/conversas", tags=["Conversas"])

@router.post("/")
def criar_conversa(nome: str, tipo: str, db: Session = Depends(get_db)):
    conversa = models.Conversa(nome=nome, tipo=tipo)
    db.add(conversa)
    db.commit()
    db.refresh(conversa)
    return conversa

@router.get("/")
def listar_conversas(db: Session = Depends(get_db)):
    return db.query(models.Conversa).all()
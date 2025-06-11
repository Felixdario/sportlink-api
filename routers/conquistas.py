from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/conquistas", tags=["Conquistas"])

@router.post("/")
def criar_conquista(atleta_id: int, nome: str, descricao: str, icone: str, db: Session = Depends(get_db)):
    conquista = models.Conquista(atleta_id=atleta_id, nome=nome, descricao=descricao, icone=icone)
    db.add(conquista)
    db.commit()
    db.refresh(conquista)
    return conquista

@router.get("/")
def listar_conquistas(db: Session = Depends(get_db)):
    return db.query(models.Conquista).all()
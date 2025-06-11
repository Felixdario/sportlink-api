from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/competicao_regras", tags=["Regras de Competição"])

@router.post("/")
def adicionar_regra(competicao_id: int, regra: str, db: Session = Depends(get_db)):
    nova_regra = models.CompeticaoRegra(competicao_id=competicao_id, regra=regra)
    db.add(nova_regra)
    db.commit()
    db.refresh(nova_regra)
    return nova_regra

@router.get("/")
def listar_regras(db: Session = Depends(get_db)):
    return db.query(models.CompeticaoRegra).all()
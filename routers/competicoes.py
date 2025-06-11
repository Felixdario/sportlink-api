from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/competicoes", tags=["Competições"])

@router.post("/")
def criar_competicao(
    nome: str,
    esporte_id: int,
    organizador_id: int,
    db: Session = Depends(get_db)
):
    if not db.query(models.Esporte).filter(models.Esporte.id == esporte_id).first():
        raise HTTPException(status_code=404, detail="Esporte não encontrado")
    if not db.query(models.Usuario).filter(models.Usuario.id == organizador_id).first():
        raise HTTPException(status_code=404, detail="Organizador não encontrado")
    competicao = models.Competicao(
        nome=nome,
        esporte_id=esporte_id,
        organizador_id=organizador_id
    )
    db.add(competicao)
    db.commit()
    db.refresh(competicao)
    return competicao

@router.get("/")
def listar_competicoes(db: Session = Depends(get_db)):
    return db.query(models.Competicao).all()
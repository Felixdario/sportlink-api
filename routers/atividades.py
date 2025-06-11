from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
import models
from getdb import get_db 

router = APIRouter(prefix="/atividades", tags=["Atividades"])

@router.post("/")
def criar_atividade(
    tipo: str,
    nome: str,
    data: str,
    local: str,
    quadra_id: int,
    organizador_id: int,
    db: Session = Depends(get_db)
):
    atividade = models.Atividade(
        tipo=tipo,
        nome=nome,
        data=data,
        local=local,
        quadra_id=quadra_id,
        organizador_id=organizador_id
    )
    db.add(atividade)
    db.commit()
    db.refresh(atividade)
    return atividade

@router.get("/")
def listar_atividades(db: Session = Depends(get_db)):
    return db.query(models.Atividade).all()

@router.post("/participar/")
def participar_atividade(atividade_id: int, usuario_id: int, db: Session = Depends(get_db)):
    participante = models.AtividadeParticipante(
        atividade_id=atividade_id,
        usuario_id=usuario_id
    )
    db.add(participante)
    db.commit()
    db.refresh(participante)
    return participante

@router.get("/participantes/")
def listar_participantes(atividade_id: int, db: Session = Depends(get_db)):
    return db.query(models.AtividadeParticipante).filter(models.AtividadeParticipante.atividade_id == atividade_id).all()
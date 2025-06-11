from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/competicao_participantes", tags=["Participantes de Competição"])

@router.post("/")
def inscrever_atleta(competicao_id: int, atleta_id: int, db: Session = Depends(get_db)):
    participante = models.CompeticaoParticipante(
        competicao_id=competicao_id,
        atleta_id=atleta_id
    )
    db.add(participante)
    db.commit()
    db.refresh(participante)
    return participante

@router.get("/")
def listar_participantes(db: Session = Depends(get_db)):
    return db.query(models.CompeticaoParticipante).all()
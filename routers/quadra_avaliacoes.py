from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/quadra_avaliacoes", tags=["Avaliações de Quadras"])

@router.post("/")
def avaliar_quadra(quadra_id: int, usuario_id: int, nota: int, comentario: str = "", db: Session = Depends(get_db)):
    if nota < 1 or nota > 5:
        raise HTTPException(status_code=400, detail="Nota deve ser entre 1 e 5")
    avaliacao = models.QuadraAvaliacao(
        quadra_id=quadra_id,
        usuario_id=usuario_id,
        nota=nota,
        comentario=comentario
    )
    db.add(avaliacao)
    db.commit()
    db.refresh(avaliacao)
    return avaliacao

@router.get("/")
def listar_avaliacoes(db: Session = Depends(get_db)):
    return db.query(models.QuadraAvaliacao).all()
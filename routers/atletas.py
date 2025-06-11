from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/atletas", tags=["Atletas"])

@router.post("/")
def criar_atleta(usuario_id: int, nivel: str = None, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if db.query(models.Atleta).filter(models.Atleta.usuario_id == usuario_id).first():
        raise HTTPException(status_code=400, detail="Usuário já possui perfil de atleta")
    atleta = models.Atleta(usuario_id=usuario_id, nivel=nivel)
    db.add(atleta)
    db.commit()
    db.refresh(atleta)
    return atleta

@router.get("/")
def listar_atletas(db: Session = Depends(get_db)):
    return db.query(models.Atleta).all()
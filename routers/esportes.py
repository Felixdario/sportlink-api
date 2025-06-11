from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from getdb import get_db 

router = APIRouter(prefix="/esportes", tags=["Esportes"])

@router.post("/")
def criar_esporte(nome: str, db: Session = Depends(get_db)):
    if db.query(models.Esporte).filter(models.Esporte.nome == nome).first():
        raise HTTPException(status_code=400, detail="Esporte já cadastrado")
    esporte = models.Esporte(nome=nome)
    db.add(esporte)
    db.commit()
    db.refresh(esporte)
    return esporte

@router.get("/")
def listar_esportes(db: Session = Depends(get_db)):
    return db.query(models.Esporte).all()
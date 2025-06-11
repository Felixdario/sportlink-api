from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
from getdb import get_db 
router = APIRouter(prefix="/quadras", tags=["Quadras"])

@router.post("/")
def criar_quadra(
    nome: str,
    endereco: str,
    dono_id: int,
    esportes_ids: List[int] = [],
    db: Session = Depends(get_db)
):
    quadra = models.Quadra(nome=nome, endereco=endereco, dono_id=dono_id)
    if esportes_ids:
        esportes = db.query(models.Esporte).filter(models.Esporte.id.in_(esportes_ids)).all()
        quadra.esportes = esportes
    db.add(quadra)
    db.commit()
    db.refresh(quadra)
    return quadra

@router.get("/")
def listar_quadras(db: Session = Depends(get_db)):
    return db.query(models.Quadra).all()
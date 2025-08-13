from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import models
from getdb import get_db 
router = APIRouter(prefix="/quadras", tags=["Quadras"])

@router.post("/")
def criar_quadra(
    nome: str,
    preco: str,
    descricao: str,
    endereco: str,
    dono_id: int,
    esportes_ids: List[int] = [],
    comodidades: Optional[str] = None,
    db: Session = Depends(get_db)
):
    quadra = models.Quadra(
        nome=nome, 
        preco=preco,
        endereco=endereco, 
        dono_id=dono_id,
        descricao=descricao,
        comodidades=comodidades
    )
    if esportes_ids:
        esportes = db.query(models.Esporte).filter(models.Esporte.id.in_(esportes_ids)).all()
        quadra.esportes = esportes
    db.add(quadra)
    db.commit()
    db.refresh(quadra)
    return quadra

@router.get("/")
def listar_quadras(db: Session = Depends(get_db)):
    quadras = db.query(models.Quadra).all()
    return quadras

@router.get("/{quadra_id}")
def obter_quadra(quadra_id: int, db: Session = Depends(get_db)):
    quadra = db.query(models.Quadra).filter(models.Quadra.id == quadra_id).first()
    if not quadra:
        raise HTTPException(status_code=404, detail="Quadra não encontrada")
    return quadra
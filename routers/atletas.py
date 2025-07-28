from pydantic import BaseModel

router = APIRouter(prefix="/atletas", tags=["Atletas"])
class AtletaRankingOut(BaseModel):
    atleta_id: int
    usuario_id: int
    nome: str
    nivel: str | None = None
    pontos: int
    conquistas: int
    vitorias: int
    cidade: str | None = None
    esportes: list[str] = []

    class Config:
        orm_mode = True

@router.get("/ranking/", response_model=list[AtletaRankingOut])
def ranking_atletas(
    criterio: str = "pontos",  # "pontos", "conquistas" ou "vitorias"
    db: Session = Depends(get_db)
):
    if criterio not in ("pontos", "conquistas", "vitorias"):
        raise HTTPException(status_code=400, detail="Critério inválido")
    atletas = db.query(models.Atleta).all()
    # Ordena pelo critério escolhido (decrescente)
    atletas_ordenados = sorted(
        atletas,
        key=lambda a: getattr(a, criterio),
        reverse=True
    )
    # Monta resposta com dados do usuário
    return [
        AtletaRankingOut(
            atleta_id=a.id,
            usuario_id=a.usuario_id,
            nome=a.usuario.nome if a.usuario else "",
            nivel=a.nivel,
            pontos=a.pontos,
            conquistas=a.conquistas,
            vitorias=a.vitorias,
            cidade=a.usuario.cidade if a.usuario and hasattr(a.usuario, "cidade") else None,
            esportes=[e.nome for e in getattr(a, "esportes", [])] if hasattr(a, "esportes") else []
        ) for a in atletas_ordenados
    ]
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from getdb import get_db 


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
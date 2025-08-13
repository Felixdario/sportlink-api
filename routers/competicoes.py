from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models
from getdb import get_db 
from sqlalchemy import func, text

router = APIRouter(prefix="/competicoes", tags=["Competições"])

@router.post("/")
def criar_competicao(
    nome: str,
    descricao: str,
    esporte_id: int,
    categoria: str,
    formato: str,
    vagas: int,
    minimo_participantes: int,
    permite_equipes: bool,
    data_inicio: datetime,
    data_fim: datetime,
    data_fim_inscricoes: datetime,
    premio: str = None,
    taxa_inscricao: str = None,
    requisitos: str = None,
    nivel_minimo: str = None,
    nivel_maximo: str = None,
    quadra_id: int = None,
    publica: bool = True,
    inscricoes_automaticas: bool = True,
    regras: List[str] = [],
    organizador_id: int = None,
    db: Session = Depends(get_db)
):
    # Validações
    if not db.query(models.Esporte).filter(models.Esporte.id == esporte_id).first():
        raise HTTPException(status_code=404, detail="Esporte não encontrado")
    if organizador_id and not db.query(models.Usuario).filter(models.Usuario.id == organizador_id).first():
        raise HTTPException(status_code=404, detail="Organizador não encontrado")
    if quadra_id and not db.query(models.Quadra).filter(models.Quadra.id == quadra_id).first():
        raise HTTPException(status_code=404, detail="Quadra não encontrada")
    
    # Criar competição
    competicao = models.Competicao(
        nome=nome,
        descricao=descricao,
        esporte_id=esporte_id,
        categoria=categoria,
        formato=formato,
        vagas=vagas,
        minimo_participantes=minimo_participantes,
        permite_equipes=permite_equipes,
        data_inicio=data_inicio,
        data_fim=data_fim,
        data_fim_inscricoes=data_fim_inscricoes,
        quadra_id=quadra_id,
        premio=premio,
        taxa_inscricao=taxa_inscricao,
        requisitos=requisitos,
        nivel_minimo=nivel_minimo,
        nivel_maximo=nivel_maximo,
        publica=publica,
        inscricoes_automaticas=inscricoes_automaticas,
        organizador_id=organizador_id
    )
    db.add(competicao)
    db.commit()
    db.refresh(competicao)
    
    # Adicionar regras
    if regras:
        for regra in regras:
            regra_obj = models.CompeticaoRegra(competicao_id=competicao.id, regra=regra)
            db.add(regra_obj)
        db.commit()
    
    return competicao

@router.get("/")
def listar_competicoes(
    esporte_id: Optional[int] = None, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Competicao)
    
    if esporte_id:
        query = query.filter(models.Competicao.esporte_id == esporte_id)
    if status:
        query = query.filter(models.Competicao.status == status)
    
    return query.all()

@router.get("/quadras_proximas/")
def buscar_quadras_proximas(
    latitude: float,
    longitude: float,
    esporte_id: Optional[int] = None,
    nome: Optional[str] = None,
    raio_km: float = 10.0,
    db: Session = Depends(get_db)
):
    """
    Busca quadras próximas a um local específico.
    
    - `latitude` e `longitude`: Coordenadas do local de referência
    - `esporte_id`: Filtrar por esporte específico
    - `nome`: Filtrar por nome da quadra
    - `raio_km`: Raio de busca em quilômetros (padrão: 10km)
    """
    # A fórmula Haversine calcula a distância entre dois pontos em uma esfera
    # 6371 é o raio da Terra em km
    distance_formula = text(
        "6371 * 2 * ASIN(SQRT("
        "POWER(SIN((radians(:lat) - radians(latitude)) / 2), 2) + "
        "COS(radians(:lat)) * COS(radians(latitude)) * "
        "POWER(SIN((radians(:lng) - radians(longitude)) / 2), 2)"
        "))"
    ).bindparams(lat=latitude, lng=longitude)
    
    query = db.query(
        models.Quadra,
        func.round(distance_formula, 2).label("distancia_km")
    ).filter(
        text("distancia_km <= :raio")
    ).params(raio=raio_km)
    
    # Filtros adicionais
    if esporte_id:
        query = query.join(models.Quadra.esportes).filter(models.Esporte.id == esporte_id)
    
    if nome:
        query = query.filter(models.Quadra.nome.ilike(f"%{nome}%"))
    
    # Ordenar por distância
    query = query.order_by(text("distancia_km"))
    
    result = []
    for quadra, distancia in query:
        quadra_dict = {
            "id": quadra.id,
            "nome": quadra.nome,
            "endereco": quadra.endereco,
            "preco": quadra.preco,
            "distancia_km": distancia,
            "latitude": float(quadra.latitude) if quadra.latitude else None,
            "longitude": float(quadra.longitude) if quadra.longitude else None
        }
        result.append(quadra_dict)
    
    return result

@router.get("/{competicao_id}")
def obter_competicao(competicao_id: int, db: Session = Depends(get_db)):
    """
    Retorna detalhes de uma competição específica, incluindo regras e informações da quadra
    """
    competicao = db.query(models.Competicao).filter(models.Competicao.id == competicao_id).first()
    if not competicao:
        raise HTTPException(status_code=404, detail="Competição não encontrada")
    
    # Obter regras da competição
    regras = db.query(models.CompeticaoRegra).filter(
        models.CompeticaoRegra.competicao_id == competicao_id
    ).all()
    
    # Obter informações da quadra se houver
    quadra = None
    if competicao.quadra_id:
        quadra = db.query(models.Quadra).filter(models.Quadra.id == competicao.quadra_id).first()
    
    # Obter esporte
    esporte = db.query(models.Esporte).filter(models.Esporte.id == competicao.esporte_id).first()
    
    # Montar resposta
    result = {
        "competicao": competicao,
        "regras": [r.regra for r in regras],
        "quadra": quadra,
        "esporte": esporte.nome if esporte else None
    }
    
    return result
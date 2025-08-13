from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import models
from getdb import get_db
from datetime import datetime

router = APIRouter(prefix="/equipes", tags=["Equipes"])

@router.post("/")
def criar_equipe(
    nome: str,
    competicao_id: int,
    capitao_id: int,
    descricao: Optional[str] = None,
    logo: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova equipe para uma competição
    """
    # Verificar se competição existe
    competicao = db.query(models.Competicao).filter(models.Competicao.id == competicao_id).first()
    if not competicao:
        raise HTTPException(status_code=404, detail="Competição não encontrada")
    
    # Verificar se competição permite equipes
    if not competicao.permite_equipes:
        raise HTTPException(status_code=400, detail="Esta competição não aceita equipes")
    
    # Verificar se atleta existe
    atleta = db.query(models.Atleta).filter(models.Atleta.id == capitao_id).first()
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se atleta já é capitão de outra equipe na mesma competição
    capitao_existente = db.query(models.Equipe).filter(
        models.Equipe.competicao_id == competicao_id,
        models.Equipe.capitao_id == capitao_id
    ).first()
    
    if capitao_existente:
        raise HTTPException(
            status_code=400, 
            detail="Este atleta já é capitão de outra equipe nesta competição"
        )
    
    # Criar equipe
    equipe = models.Equipe(
        nome=nome,
        descricao=descricao,
        logo=logo,
        competicao_id=competicao_id,
        capitao_id=capitao_id
    )
    db.add(equipe)
    db.commit()
    db.refresh(equipe)
    
    # Adicionar capitão como membro da equipe
    membro = models.MembroEquipe(
        equipe_id=equipe.id,
        atleta_id=capitao_id,
        funcao="capitao"
    )
    db.add(membro)
    
    # Inscrever equipe na competição, se ainda não estiver inscrito
    inscricao = db.query(models.CompeticaoParticipante).filter(
        models.CompeticaoParticipante.competicao_id == competicao_id,
        models.CompeticaoParticipante.atleta_id == capitao_id
    ).first()
    
    if not inscricao:
        status = "aprovado" if competicao.inscricoes_automaticas else "pendente"
        inscricao = models.CompeticaoParticipante(
            competicao_id=competicao_id,
            atleta_id=capitao_id,
            status=status
        )
        db.add(inscricao)
    
    db.commit()
    
    return equipe

@router.post("/{equipe_id}/membros")
def adicionar_membro(
    equipe_id: int,
    atleta_id: int,
    funcao: str = "jogador",
    db: Session = Depends(get_db)
):
    """
    Adiciona um atleta como membro de uma equipe
    """
    # Verificar se equipe existe
    equipe = db.query(models.Equipe).filter(models.Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=404, detail="Equipe não encontrada")
    
    # Verificar se atleta existe
    atleta = db.query(models.Atleta).filter(models.Atleta.id == atleta_id).first()
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se atleta já é membro de outra equipe na mesma competição
    membro_existente = db.query(models.MembroEquipe).join(
        models.Equipe, models.MembroEquipe.equipe_id == models.Equipe.id
    ).filter(
        models.Equipe.competicao_id == equipe.competicao_id,
        models.MembroEquipe.atleta_id == atleta_id
    ).first()
    
    if membro_existente:
        if membro_existente.equipe_id == equipe_id:
            raise HTTPException(status_code=400, detail="Atleta já é membro desta equipe")
        else:
            raise HTTPException(
                status_code=400, 
                detail="Atleta já é membro de outra equipe nesta competição"
            )
    
    # Adicionar membro à equipe
    membro = models.MembroEquipe(
        equipe_id=equipe_id,
        atleta_id=atleta_id,
        funcao=funcao
    )
    db.add(membro)
    
    # Inscrever atleta na competição, se ainda não estiver inscrito
    inscricao = db.query(models.CompeticaoParticipante).filter(
        models.CompeticaoParticipante.competicao_id == equipe.competicao_id,
        models.CompeticaoParticipante.atleta_id == atleta_id
    ).first()
    
    competicao = db.query(models.Competicao).filter(
        models.Competicao.id == equipe.competicao_id
    ).first()
    
    if not inscricao and competicao:
        status = "aprovado" if competicao.inscricoes_automaticas else "pendente"
        inscricao = models.CompeticaoParticipante(
            competicao_id=equipe.competicao_id,
            atleta_id=atleta_id,
            status=status
        )
        db.add(inscricao)
    
    db.commit()
    
    return {"mensagem": "Membro adicionado com sucesso"}

@router.get("/{equipe_id}/membros")
def listar_membros(
    equipe_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todos os membros de uma equipe
    """
    # Verificar se equipe existe
    equipe = db.query(models.Equipe).filter(models.Equipe.id == equipe_id).first()
    if not equipe:
        raise HTTPException(status_code=404, detail="Equipe não encontrada")
    
    # Listar membros
    membros = db.query(
        models.MembroEquipe, models.Atleta, models.Usuario
    ).join(
        models.Atleta, models.MembroEquipe.atleta_id == models.Atleta.id
    ).join(
        models.Usuario, models.Atleta.usuario_id == models.Usuario.id
    ).filter(
        models.MembroEquipe.equipe_id == equipe_id
    ).all()
    
    result = []
    for membro, atleta, usuario in membros:
        result.append({
            "atleta_id": atleta.id,
            "nome": usuario.nome,
            "username": usuario.username,
            "avatar": usuario.avatar,
            "funcao": membro.funcao,
            "nivel": atleta.nivel,
            "status": membro.status
        })
    
    return result

@router.get("/competicao/{competicao_id}")
def listar_equipes_competicao(
    competicao_id: int,
    db: Session = Depends(get_db)
):
    """
    Lista todas as equipes de uma competição
    """
    equipes = db.query(models.Equipe).filter(
        models.Equipe.competicao_id == competicao_id
    ).all()
    
    return equipes

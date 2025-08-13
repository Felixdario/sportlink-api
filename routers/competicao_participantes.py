from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List
import models
from getdb import get_db

router = APIRouter(prefix="/competicao_participantes", tags=["Participantes de Competição"])

@router.post("/")
def inscrever_atleta(
    competicao_id: int, 
    atleta_id: int, 
    equipe_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Inscreve um atleta em uma competição, verificando os níveis mínimos e máximos exigidos.
    
    - Se for uma competição de equipes, o parâmetro equipe_id deve ser fornecido
    - O sistema verifica se o atleta atende aos requisitos de nível
    """
    # Verificar se competição existe
    competicao = db.query(models.Competicao).filter(models.Competicao.id == competicao_id).first()
    if not competicao:
        raise HTTPException(status_code=404, detail="Competição não encontrada")
    
    # Verificar se atleta existe
    atleta = db.query(models.Atleta).filter(models.Atleta.id == atleta_id).first()
    if not atleta:
        raise HTTPException(status_code=404, detail="Atleta não encontrado")
    
    # Verificar se inscrições estão abertas
    from datetime import datetime
    if competicao.data_fim_inscricoes and datetime.now() > competicao.data_fim_inscricoes:
        raise HTTPException(status_code=400, detail="Inscrições encerradas para esta competição")
    
    # Verificar se há vagas disponíveis
    total_inscritos = db.query(models.CompeticaoParticipante).filter(
        models.CompeticaoParticipante.competicao_id == competicao_id,
        models.CompeticaoParticipante.status.in_(["pendente", "aprovado"])
    ).count()
    
    if competicao.vagas and total_inscritos >= competicao.vagas:
        raise HTTPException(status_code=400, detail="Competição com vagas esgotadas")
    
    # Verificar nível do atleta
    if competicao.nivel_minimo and (not atleta.nivel or atleta.nivel < competicao.nivel_minimo):
        raise HTTPException(status_code=400, detail=f"Nível mínimo requerido: {competicao.nivel_minimo}")
        
    if competicao.nivel_maximo and atleta.nivel and atleta.nivel > competicao.nivel_maximo:
        raise HTTPException(status_code=400, detail=f"Nível máximo permitido: {competicao.nivel_maximo}")
    
    # Verificar se é competição por equipes e se a equipe foi informada
    if competicao.permite_equipes and not equipe_id:
        raise HTTPException(status_code=400, detail="Esta competição requer participação em equipe")
    
    # Verificar se a equipe existe e pertence à competição
    if equipe_id:
        equipe = db.query(models.Equipe).filter(models.Equipe.id == equipe_id).first()
        if not equipe:
            raise HTTPException(status_code=404, detail="Equipe não encontrada")
        if equipe.competicao_id != competicao_id:
            raise HTTPException(status_code=400, detail="Esta equipe não pertence a esta competição")
        
        # Adicionar atleta à equipe
        membro_equipe = models.MembroEquipe(equipe_id=equipe_id, atleta_id=atleta_id)
        db.add(membro_equipe)
    
    # Verificar se atleta já está inscrito
    inscricao_existente = db.query(models.CompeticaoParticipante).filter(
        models.CompeticaoParticipante.competicao_id == competicao_id,
        models.CompeticaoParticipante.atleta_id == atleta_id
    ).first()
    
    if inscricao_existente:
        raise HTTPException(status_code=400, detail="Atleta já inscrito nesta competição")
    
    # Definir status da inscrição conforme configuração da competição
    status = "aprovado" if competicao.inscricoes_automaticas else "pendente"
    
    # Criar inscrição
    participante = models.CompeticaoParticipante(
        competicao_id=competicao_id,
        atleta_id=atleta_id,
        status=status
    )
    db.add(participante)
    db.commit()
    db.refresh(participante)
    
    return {
        "inscricao": participante,
        "status": status,
        "mensagem": "Inscrição realizada com sucesso" if status == "aprovado" else "Inscrição pendente de aprovação"
    }

@router.get("/")
def listar_participantes(
    competicao_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista participantes de competições com filtros opcionais
    """
    query = db.query(models.CompeticaoParticipante)
    
    if competicao_id:
        query = query.filter(models.CompeticaoParticipante.competicao_id == competicao_id)
    if status:
        query = query.filter(models.CompeticaoParticipante.status == status)
    
    return query.all()

@router.post("/{participante_id}/aprovar")
def aprovar_inscricao(
    participante_id: int,
    db: Session = Depends(get_db)
):
    """
    Aprova uma inscrição pendente
    """
    participante = db.query(models.CompeticaoParticipante).filter(
        models.CompeticaoParticipante.id == participante_id
    ).first()
    
    if not participante:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
        
    if participante.status != "pendente":
        raise HTTPException(status_code=400, detail="Esta inscrição não está pendente de aprovação")
    
    participante.status = "aprovado"
    db.commit()
    db.refresh(participante)
    
    return {"mensagem": "Inscrição aprovada com sucesso", "inscricao": participante}

@router.post("/{participante_id}/rejeitar")
def rejeitar_inscricao(
    participante_id: int,
    motivo: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Rejeita uma inscrição pendente
    """
    participante = db.query(models.CompeticaoParticipante).filter(
        models.CompeticaoParticipante.id == participante_id
    ).first()
    
    if not participante:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")
        
    if participante.status != "pendente":
        raise HTTPException(status_code=400, detail="Esta inscrição não está pendente de aprovação")
    
    participante.status = "rejeitado"
    db.commit()
    
    return {"mensagem": "Inscrição rejeitada", "motivo": motivo}
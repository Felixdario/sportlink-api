from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import models
from getdb import get_db
from datetime import datetime

router = APIRouter(prefix="/partidas", tags=["Partidas"])

@router.post("/")
def criar_partida(
    competicao_id: int,
    fase: str,
    data: datetime,
    quadra_id: Optional[int] = None,
    local: Optional[str] = None,
    equipe1_id: Optional[int] = None,
    equipe2_id: Optional[int] = None,
    atleta1_id: Optional[int] = None,
    atleta2_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova partida para uma competição
    
    - Pode ser uma partida entre equipes (equipe1_id e equipe2_id) ou entre atletas (atleta1_id e atleta2_id)
    - A competição deve existir
    - Se a competição não permitir equipes, equipe1_id e equipe2_id devem ser nulos
    - Se a competição exigir equipes, atleta1_id e atleta2_id devem ser nulos
    """
    # Verificar se competição existe
    competicao = db.query(models.Competicao).filter(models.Competicao.id == competicao_id).first()
    if not competicao:
        raise HTTPException(status_code=404, detail="Competição não encontrada")
    
    # Validar tipo de partida (equipe ou individual)
    if competicao.permite_equipes:
        if not equipe1_id or not equipe2_id:
            raise HTTPException(status_code=400, detail="Partida deve ser entre equipes")
        if atleta1_id or atleta2_id:
            raise HTTPException(status_code=400, detail="Partida não deve incluir atletas individuais")
            
        # Verificar se equipes existem
        equipe1 = db.query(models.Equipe).filter(models.Equipe.id == equipe1_id).first()
        equipe2 = db.query(models.Equipe).filter(models.Equipe.id == equipe2_id).first()
        
        if not equipe1:
            raise HTTPException(status_code=404, detail="Equipe 1 não encontrada")
        if not equipe2:
            raise HTTPException(status_code=404, detail="Equipe 2 não encontrada")
            
        if equipe1.competicao_id != competicao_id or equipe2.competicao_id != competicao_id:
            raise HTTPException(status_code=400, detail="As equipes devem pertencer à competição")
    else:
        if equipe1_id or equipe2_id:
            raise HTTPException(status_code=400, detail="Partida deve ser entre atletas individuais")
        if not atleta1_id or not atleta2_id:
            raise HTTPException(status_code=400, detail="Partida deve incluir atletas individuais")
            
        # Verificar se atletas existem e estão inscritos na competição
        for atleta_id in [atleta1_id, atleta2_id]:
            if atleta_id:
                inscricao = db.query(models.CompeticaoParticipante).filter(
                    models.CompeticaoParticipante.competicao_id == competicao_id,
                    models.CompeticaoParticipante.atleta_id == atleta_id,
                    models.CompeticaoParticipante.status == "aprovado"
                ).first()
                
                if not inscricao:
                    raise HTTPException(status_code=400, detail=f"Atleta {atleta_id} não está inscrito na competição")
    
    # Verificar se quadra existe, se fornecida
    if quadra_id:
        quadra = db.query(models.Quadra).filter(models.Quadra.id == quadra_id).first()
        if not quadra:
            raise HTTPException(status_code=404, detail="Quadra não encontrada")
    
    # Criar partida
    partida = models.Partida(
        competicao_id=competicao_id,
        fase=fase,
        data=data,
        local=local,
        quadra_id=quadra_id,
        equipe1_id=equipe1_id,
        equipe2_id=equipe2_id,
        atleta1_id=atleta1_id,
        atleta2_id=atleta2_id,
        status="agendada"
    )
    db.add(partida)
    db.commit()
    db.refresh(partida)
    
    return partida

@router.get("/competicao/{competicao_id}")
def listar_partidas_competicao(
    competicao_id: int,
    fase: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista todas as partidas de uma competição
    """
    query = db.query(models.Partida).filter(models.Partida.competicao_id == competicao_id)
    
    if fase:
        query = query.filter(models.Partida.fase == fase)
    if status:
        query = query.filter(models.Partida.status == status)
    
    partidas = query.all()
    
    # Enriquecer dados das partidas
    result = []
    for partida in partidas:
        partida_dict = {
            "id": partida.id,
            "fase": partida.fase,
            "data": partida.data,
            "local": partida.local,
            "status": partida.status,
            "quadra": None,
            "equipe1": None,
            "equipe2": None,
            "atleta1": None,
            "atleta2": None,
            "resultado": None
        }
        
        # Incluir dados da quadra
        if partida.quadra_id:
            quadra = db.query(models.Quadra).filter(models.Quadra.id == partida.quadra_id).first()
            if quadra:
                partida_dict["quadra"] = {
                    "id": quadra.id,
                    "nome": quadra.nome,
                    "endereco": quadra.endereco
                }
        
        # Incluir dados das equipes
        if partida.equipe1_id:
            equipe1 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe1_id).first()
            if equipe1:
                partida_dict["equipe1"] = {
                    "id": equipe1.id,
                    "nome": equipe1.nome
                }
                
        if partida.equipe2_id:
            equipe2 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe2_id).first()
            if equipe2:
                partida_dict["equipe2"] = {
                    "id": equipe2.id,
                    "nome": equipe2.nome
                }
        
        # Incluir dados dos atletas
        if partida.atleta1_id:
            atleta1 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta1_id).first()
            if atleta1:
                partida_dict["atleta1"] = {
                    "id": atleta1.id,
                    "nome": atleta1.usuario.nome if atleta1.usuario else None
                }
                
        if partida.atleta2_id:
            atleta2 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta2_id).first()
            if atleta2:
                partida_dict["atleta2"] = {
                    "id": atleta2.id,
                    "nome": atleta2.usuario.nome if atleta2.usuario else None
                }
        
        # Incluir resultado
        if partida.status == "finalizada":
            partida_dict["resultado"] = {
                "equipe1": partida.resultado_equipe1,
                "equipe2": partida.resultado_equipe2
            }
        
        result.append(partida_dict)
    
    return result

@router.get("/{partida_id}")
def obter_partida(
    partida_id: int,
    db: Session = Depends(get_db)
):
    """
    Retorna detalhes de uma partida específica
    """
    partida = db.query(models.Partida).filter(models.Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    # Construir resposta detalhada
    result = {
        "id": partida.id,
        "competicao_id": partida.competicao_id,
        "fase": partida.fase,
        "data": partida.data,
        "local": partida.local,
        "status": partida.status,
        "quadra": None,
        "equipe1": None,
        "equipe2": None,
        "atleta1": None,
        "atleta2": None,
        "resultado": None,
        "eventos": []
    }
    
    # Incluir dados da quadra
    if partida.quadra_id:
        quadra = db.query(models.Quadra).filter(models.Quadra.id == partida.quadra_id).first()
        if quadra:
            result["quadra"] = {
                "id": quadra.id,
                "nome": quadra.nome,
                "endereco": quadra.endereco
            }
    
    # Incluir dados das equipes
    if partida.equipe1_id:
        equipe1 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe1_id).first()
        if equipe1:
            result["equipe1"] = {
                "id": equipe1.id,
                "nome": equipe1.nome
            }
            
    if partida.equipe2_id:
        equipe2 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe2_id).first()
        if equipe2:
            result["equipe2"] = {
                "id": equipe2.id,
                "nome": equipe2.nome
            }
    
    # Incluir dados dos atletas
    if partida.atleta1_id:
        atleta1 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta1_id).first()
        if atleta1:
            result["atleta1"] = {
                "id": atleta1.id,
                "nome": atleta1.usuario.nome if atleta1.usuario else None
            }
            
    if partida.atleta2_id:
        atleta2 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta2_id).first()
        if atleta2:
            result["atleta2"] = {
                "id": atleta2.id,
                "nome": atleta2.usuario.nome if atleta2.usuario else None
            }
    
    # Incluir resultado e eventos
    if partida.status == "finalizada":
        result["resultado"] = {
            "equipe1": partida.resultado_equipe1,
            "equipe2": partida.resultado_equipe2,
            "detalhes": partida.detalhes
        }
    
    # Listar eventos da partida
    eventos = db.query(models.EventoPartida).filter(
        models.EventoPartida.partida_id == partida_id
    ).order_by(models.EventoPartida.id).all()
    
    for evento in eventos:
        evento_dict = {
            "id": evento.id,
            "tipo": evento.tipo,
            "tempo": evento.tempo,
            "descricao": evento.descricao,
            "valor": evento.valor,
            "atleta": None,
            "equipe": None
        }
        
        # Incluir dados do atleta
        if evento.atleta_id:
            atleta = db.query(models.Atleta).join(models.Usuario).filter(
                models.Atleta.id == evento.atleta_id
            ).first()
            if atleta and atleta.usuario:
                evento_dict["atleta"] = {
                    "id": atleta.id,
                    "nome": atleta.usuario.nome
                }
        
        # Incluir dados da equipe
        if evento.equipe_id:
            equipe = db.query(models.Equipe).filter(models.Equipe.id == evento.equipe_id).first()
            if equipe:
                evento_dict["equipe"] = {
                    "id": equipe.id,
                    "nome": equipe.nome
                }
        
        result["eventos"].append(evento_dict)
    
    return result

@router.post("/{partida_id}/resultado")
def registrar_resultado(
    partida_id: int,
    resultado: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Registra o resultado de uma partida
    
    O corpo da requisição deve conter:
    - resultado_equipe1: int (obrigatório)
    - resultado_equipe2: int (obrigatório)
    - detalhes: str (opcional)
    - eventos: list (opcional) - lista de eventos da partida
    """
    # Verificar se partida existe
    partida = db.query(models.Partida).filter(models.Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    # Verificar se partida já está finalizada
    if partida.status == "finalizada":
        raise HTTPException(status_code=400, detail="Esta partida já está finalizada")
    
    # Extrair dados do resultado
    resultado_equipe1 = resultado.get("resultado_equipe1")
    resultado_equipe2 = resultado.get("resultado_equipe2")
    detalhes = resultado.get("detalhes")
    eventos = resultado.get("eventos", [])
    
    if resultado_equipe1 is None or resultado_equipe2 is None:
        raise HTTPException(status_code=400, detail="Resultados incompletos")
    
    # Atualizar partida
    partida.resultado_equipe1 = resultado_equipe1
    partida.resultado_equipe2 = resultado_equipe2
    partida.detalhes = detalhes
    partida.status = "finalizada"
    
    # Registrar eventos
    for evento in eventos:
        evento_obj = models.EventoPartida(
            partida_id=partida_id,
            tipo=evento.get("tipo"),
            tempo=evento.get("tempo"),
            descricao=evento.get("descricao"),
            atleta_id=evento.get("atleta_id"),
            equipe_id=evento.get("equipe_id"),
            valor=evento.get("valor")
        )
        db.add(evento_obj)
    
    # Atualizar estatísticas dos atletas
    # Para competições individuais
    if partida.atleta1_id and partida.atleta2_id:
        atleta1 = db.query(models.Atleta).filter(models.Atleta.id == partida.atleta1_id).first()
        atleta2 = db.query(models.Atleta).filter(models.Atleta.id == partida.atleta2_id).first()
        
        if atleta1 and atleta2:
            # Determinar vencedor
            if resultado_equipe1 > resultado_equipe2:
                atleta1.vitorias += 1
                atleta2.derrotas += 1
                atleta1.pontos += 3
            elif resultado_equipe1 < resultado_equipe2:
                atleta2.vitorias += 1
                atleta1.derrotas += 1
                atleta2.pontos += 3
            else:
                atleta1.empates += 1
                atleta2.empates += 1
                atleta1.pontos += 1
                atleta2.pontos += 1
    
    db.commit()
    
    return {"mensagem": "Resultado registrado com sucesso"}

@router.post("/{partida_id}/evento")
def adicionar_evento(
    partida_id: int,
    evento: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Adiciona um evento a uma partida
    
    O corpo da requisição deve conter:
    - tipo: str (obrigatório) - tipo de evento (gol, cartão, falta, etc)
    - tempo: str (obrigatório) - tempo do evento (ex: '15:30', '2T 23:15')
    - descricao: str (opcional) - descrição do evento
    - atleta_id: int (opcional) - id do atleta envolvido no evento
    - equipe_id: int (opcional) - id da equipe envolvida no evento
    - valor: int (opcional) - valor numérico do evento (pontos, etc)
    """
    # Verificar se partida existe
    partida = db.query(models.Partida).filter(models.Partida.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    
    # Verificar se partida está em andamento ou finalizada
    if partida.status == "agendada":
        raise HTTPException(status_code=400, detail="Esta partida ainda não começou")
    
    # Criar evento
    evento_obj = models.EventoPartida(
        partida_id=partida_id,
        tipo=evento.get("tipo"),
        tempo=evento.get("tempo"),
        descricao=evento.get("descricao"),
        atleta_id=evento.get("atleta_id"),
        equipe_id=evento.get("equipe_id"),
        valor=evento.get("valor")
    )
    db.add(evento_obj)
    db.commit()
    db.refresh(evento_obj)
    
    return evento_obj

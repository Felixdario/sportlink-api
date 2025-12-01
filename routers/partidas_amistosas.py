from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import models
from getdb import get_db
from datetime import datetime

router = APIRouter(prefix="/partidas_amistosas", tags=["Partidas Amistosas"])

@router.post("/")
def criar_partida_amistosa(
    esporte_id: Optional[int] = None,
    data: datetime = None,
    quadra_id: Optional[int] = None,
    local: Optional[str] = None,
    equipe1_id: Optional[int] = None,
    equipe2_id: Optional[int] = None,
    atleta1_id: Optional[int] = None,
    atleta2_id: Optional[int] = None,
    organizador_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Cria uma partida amistosa (entre equipes ou entre atletas)"""
    # Validar quadra
    if quadra_id:
        quadra = db.query(models.Quadra).filter(models.Quadra.id == quadra_id).first()
        if not quadra:
            raise HTTPException(status_code=404, detail="Quadra não encontrada")

    # Validar organizador
    if organizador_id:
        user = db.query(models.Usuario).filter(models.Usuario.id == organizador_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Organizador não encontrado")

    # Validar tipo: se houver equipes, não pode haver atletas e vice-versa
    if (equipe1_id or equipe2_id) and (atleta1_id or atleta2_id):
        raise HTTPException(status_code=400, detail="Partida deve ser entre equipes ou entre atletas, não ambos")

    if equipe1_id or equipe2_id:
        if not (equipe1_id and equipe2_id):
            raise HTTPException(status_code=400, detail="Devem ser informadas as duas equipes")
        equipe1 = db.query(models.Equipe).filter(models.Equipe.id == equipe1_id).first()
        equipe2 = db.query(models.Equipe).filter(models.Equipe.id == equipe2_id).first()
        if not equipe1 or not equipe2:
            raise HTTPException(status_code=404, detail="Uma ou ambas as equipes não foram encontradas")

    if atleta1_id or atleta2_id:
        if not (atleta1_id and atleta2_id):
            raise HTTPException(status_code=400, detail="Devem ser informados os dois atletas")
        atleta1 = db.query(models.Atleta).filter(models.Atleta.id == atleta1_id).first()
        atleta2 = db.query(models.Atleta).filter(models.Atleta.id == atleta2_id).first()
        if not atleta1 or not atleta2:
            raise HTTPException(status_code=404, detail="Um ou ambos os atletas não foram encontrados")

    partida = models.PartidaAmistosa(
        esporte_id=esporte_id,
        data=data,
        quadra_id=quadra_id,
        local=local,
        equipe1_id=equipe1_id,
        equipe2_id=equipe2_id,
        atleta1_id=atleta1_id,
        atleta2_id=atleta2_id,
        organizador_id=organizador_id,
        status="agendada"
    )
    db.add(partida)
    db.commit()
    db.refresh(partida)

    return partida


@router.get("/")
def listar_partidas_amistosas(
    esporte_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.PartidaAmistosa)
    if esporte_id:
        query = query.filter(models.PartidaAmistosa.esporte_id == esporte_id)
    if status:
        query = query.filter(models.PartidaAmistosa.status == status)
    partidas = query.all()

    result = []
    for partida in partidas:
        partida_dict = {
            "id": partida.id,
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
        if partida.quadra_id:
            quadra = db.query(models.Quadra).filter(models.Quadra.id == partida.quadra_id).first()
            if quadra:
                partida_dict["quadra"] = {"id": quadra.id, "nome": quadra.nome, "endereco": quadra.endereco}
        if partida.equipe1_id:
            equipe1 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe1_id).first()
            if equipe1:
                partida_dict["equipe1"] = {"id": equipe1.id, "nome": equipe1.nome}
        if partida.equipe2_id:
            equipe2 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe2_id).first()
            if equipe2:
                partida_dict["equipe2"] = {"id": equipe2.id, "nome": equipe2.nome}
        if partida.atleta1_id:
            atleta1 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta1_id).first()
            if atleta1:
                partida_dict["atleta1"] = {"id": atleta1.id, "nome": atleta1.usuario.nome if atleta1.usuario else None}
        if partida.atleta2_id:
            atleta2 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta2_id).first()
            if atleta2:
                partida_dict["atleta2"] = {"id": atleta2.id, "nome": atleta2.usuario.nome if atleta2.usuario else None}
        if partida.status == "finalizada":
            partida_dict["resultado"] = {"equipe1": partida.resultado_equipe1, "equipe2": partida.resultado_equipe2}
        result.append(partida_dict)
    return result


@router.get("/{partida_id}")
def obter_partida_amistosa(partida_id: int, db: Session = Depends(get_db)):
    partida = db.query(models.PartidaAmistosa).filter(models.PartidaAmistosa.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida amistosa não encontrada")

    result = {
        "id": partida.id,
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
    if partida.quadra_id:
        quadra = db.query(models.Quadra).filter(models.Quadra.id == partida.quadra_id).first()
        if quadra:
            result["quadra"] = {"id": quadra.id, "nome": quadra.nome, "endereco": quadra.endereco}
    if partida.equipe1_id:
        equipe1 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe1_id).first()
        if equipe1:
            result["equipe1"] = {"id": equipe1.id, "nome": equipe1.nome}
    if partida.equipe2_id:
        equipe2 = db.query(models.Equipe).filter(models.Equipe.id == partida.equipe2_id).first()
        if equipe2:
            result["equipe2"] = {"id": equipe2.id, "nome": equipe2.nome}
    if partida.atleta1_id:
        atleta1 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta1_id).first()
        if atleta1:
            result["atleta1"] = {"id": atleta1.id, "nome": atleta1.usuario.nome if atleta1.usuario else None}
    if partida.atleta2_id:
        atleta2 = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == partida.atleta2_id).first()
        if atleta2:
            result["atleta2"] = {"id": atleta2.id, "nome": atleta2.usuario.nome if atleta2.usuario else None}

    eventos = db.query(models.EventoPartidaAmistosa).filter(models.EventoPartidaAmistosa.partida_id == partida_id).order_by(models.EventoPartidaAmistosa.id).all()
    for evento in eventos:
        evento_dict = {"id": evento.id, "tipo": evento.tipo, "tempo": evento.tempo, "descricao": evento.descricao, "valor": evento.valor, "atleta": None, "equipe": None}
        if evento.atleta_id:
            atleta = db.query(models.Atleta).join(models.Usuario).filter(models.Atleta.id == evento.atleta_id).first()
            if atleta and atleta.usuario:
                evento_dict["atleta"] = {"id": atleta.id, "nome": atleta.usuario.nome}
        if evento.equipe_id:
            equipe = db.query(models.Equipe).filter(models.Equipe.id == evento.equipe_id).first()
            if equipe:
                evento_dict["equipe"] = {"id": equipe.id, "nome": equipe.nome}
        result["eventos"].append(evento_dict)

    if partida.status == "finalizada":
        result["resultado"] = {"equipe1": partida.resultado_equipe1, "equipe2": partida.resultado_equipe2, "detalhes": partida.detalhes}

    return result


@router.post("/{partida_id}/resultado")
def registrar_resultado_amistosa(partida_id: int, resultado: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    partida = db.query(models.PartidaAmistosa).filter(models.PartidaAmistosa.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida amistosa não encontrada")
    if partida.status == "finalizada":
        raise HTTPException(status_code=400, detail="Esta partida já está finalizada")

    resultado_equipe1 = resultado.get("resultado_equipe1")
    resultado_equipe2 = resultado.get("resultado_equipe2")
    detalhes = resultado.get("detalhes")
    eventos = resultado.get("eventos", [])

    if resultado_equipe1 is None or resultado_equipe2 is None:
        raise HTTPException(status_code=400, detail="Resultados incompletos")

    partida.resultado_equipe1 = resultado_equipe1
    partida.resultado_equipe2 = resultado_equipe2
    partida.detalhes = detalhes
    partida.status = "finalizada"

    for evento in eventos:
        evento_obj = models.EventoPartidaAmistosa(
            partida_id=partida_id,
            tipo=evento.get("tipo"),
            tempo=evento.get("tempo"),
            descricao=evento.get("descricao"),
            atleta_id=evento.get("atleta_id"),
            equipe_id=evento.get("equipe_id"),
            valor=evento.get("valor")
        )
        db.add(evento_obj)

    # Atualizar estatísticas dos atletas (opcional para amistosas também)
    if partida.atleta1_id and partida.atleta2_id:
        atleta1 = db.query(models.Atleta).filter(models.Atleta.id == partida.atleta1_id).first()
        atleta2 = db.query(models.Atleta).filter(models.Atleta.id == partida.atleta2_id).first()
        if atleta1 and atleta2:
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
def adicionar_evento_amistosa(partida_id: int, evento: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    partida = db.query(models.PartidaAmistosa).filter(models.PartidaAmistosa.id == partida_id).first()
    if not partida:
        raise HTTPException(status_code=404, detail="Partida amistosa não encontrada")
    if partida.status == "agendada":
        raise HTTPException(status_code=400, detail="Esta partida ainda não começou")

    evento_obj = models.EventoPartidaAmistosa(
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

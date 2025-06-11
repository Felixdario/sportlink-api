from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from getdb import get_db 

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

class UsuarioCreate(BaseModel):
    nome: str
    email: str
    senha: str

@router.post("/")
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo_usuario = models.Usuario(nome=usuario.nome, email=usuario.email, senha_hash=usuario.senha)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {
        "id": novo_usuario.id,
        "nome": novo_usuario.nome,
        "email": novo_usuario.email,
        "mensagem": "Usuário criado. Agora você pode criar seu perfil de atleta ou cadastrar quadras."
    }
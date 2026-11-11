from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from getdb import get_db
from seguranca import HASH_FICTICIO, gerar_hash, verificar_senha

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
    novo_usuario = models.Usuario(nome=usuario.nome, email=usuario.email, senha_hash=gerar_hash(usuario.senha))
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return {
        "id": novo_usuario.id,
        "nome": novo_usuario.nome,
        "email": novo_usuario.email,
        "mensagem": "Usuário criado. Agora você pode criar seu perfil de atleta ou cadastrar quadras."
    }
class UsuarioLogin(BaseModel):
    email: str
    senha: str

@router.post("/login/")
def login_usuario(dados: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == dados.email).first()
    confere, precisa_regravar = verificar_senha(
        dados.senha, usuario.senha_hash if usuario else HASH_FICTICIO
    )
    if not usuario or not confere:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    if precisa_regravar:
        # Senha gravada em texto puro antes do hash: troca pelo hash no primeiro login certo.
        usuario.senha_hash = gerar_hash(dados.senha)
        db.commit()
    tipo = "usuario"
    if usuario.quadras and len(usuario.quadras) > 0:
        tipo = "dono_quadra"
    elif usuario.atleta:
        tipo = "atleta"
    return {
        "id": usuario.id,
        "nome": usuario.nome,
        "email": usuario.email,
        "tipo": tipo
    }
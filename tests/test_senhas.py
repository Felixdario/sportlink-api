import uuid

from fastapi.testclient import TestClient

import models
from database import SessionLocal
from main import app
from migration_senhas import run_migration
from seguranca import eh_hash, gerar_hash, verificar_senha

client = TestClient(app)


def _email() -> str:
    return f"{uuid.uuid4().hex}@teste.dev"


def _senha_gravada(email: str) -> str:
    db = SessionLocal()
    try:
        return db.query(models.Usuario).filter(models.Usuario.email == email).one().senha_hash
    finally:
        db.close()


def _gravar_texto_puro(email: str, senha: str) -> None:
    db = SessionLocal()
    try:
        db.add(models.Usuario(nome="Legado", email=email, senha_hash=senha))
        db.commit()
    finally:
        db.close()


def test_hash_tem_sal_e_confere():
    a, b = gerar_hash("segredo123"), gerar_hash("segredo123")
    assert a != b  # sal aleatório
    assert eh_hash(a)
    assert verificar_senha("segredo123", a) == (True, False)
    assert verificar_senha("errada", a) == (False, False)


def test_hash_corrompido_nao_confere():
    assert verificar_senha("x", "scrypt$1$2$3$nao-e-base64$!!") == (False, False)


def test_cadastro_grava_hash_e_nao_a_senha():
    email = _email()
    r = client.post("/usuarios/", json={"nome": "Ana", "email": email, "senha": "segredo123"})
    assert r.status_code == 200
    assert "senha" not in r.text and "segredo123" not in r.text
    gravado = _senha_gravada(email)
    assert gravado != "segredo123"
    assert eh_hash(gravado)


def test_login_com_hash():
    email = _email()
    client.post("/usuarios/", json={"nome": "Ana", "email": email, "senha": "segredo123"})
    assert client.post("/usuarios/login/", json={"email": email, "senha": "segredo123"}).status_code == 200
    assert client.post("/usuarios/login/", json={"email": email, "senha": "errada"}).status_code == 401


def test_email_inexistente_da_401():
    r = client.post("/usuarios/login/", json={"email": _email(), "senha": "qualquer"})
    assert r.status_code == 401


def test_senha_legada_em_texto_puro_vira_hash_no_login():
    email = _email()
    _gravar_texto_puro(email, "antiga123")
    assert client.post("/usuarios/login/", json={"email": email, "senha": "errada"}).status_code == 401
    assert _senha_gravada(email) == "antiga123"  # senha errada não regrava
    assert client.post("/usuarios/login/", json={"email": email, "senha": "antiga123"}).status_code == 200
    gravado = _senha_gravada(email)
    assert eh_hash(gravado)
    assert client.post("/usuarios/login/", json={"email": email, "senha": "antiga123"}).status_code == 200


def test_migracao_converte_texto_puro_e_e_idempotente():
    email = _email()
    _gravar_texto_puro(email, "antiga456")
    run_migration()
    gravado = _senha_gravada(email)
    assert eh_hash(gravado)
    run_migration()
    assert _senha_gravada(email) == gravado
    assert client.post("/usuarios/login/", json={"email": email, "senha": "antiga456"}).status_code == 200

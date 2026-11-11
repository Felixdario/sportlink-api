"""Troca por hash (scrypt) toda senha que ainda estiver gravada em texto puro.

Rode uma vez em cada banco que já existia antes do hash de senha:

    python migration_senhas.py

É idempotente: valores que já são hash ficam como estão.
"""

from database import SessionLocal
import models
from seguranca import eh_hash, gerar_hash


def run_migration():
    print("Iniciando migração das senhas...")
    db = SessionLocal()
    try:
        trocadas = 0
        for usuario in db.query(models.Usuario).all():
            if usuario.senha_hash and not eh_hash(usuario.senha_hash):
                usuario.senha_hash = gerar_hash(usuario.senha_hash)
                trocadas += 1
        db.commit()
        print(f"Migração concluída: {trocadas} senha(s) convertida(s) para hash.")
    except Exception as e:
        db.rollback()
        print(f"Erro durante a migração: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_migration()

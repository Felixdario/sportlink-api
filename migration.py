from database import engine
from sqlalchemy import text, inspect
import models

def run_migration():
    print("Iniciando migração do banco de dados...")
    
    # Adicionar novas colunas à tabela de quadras
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('quadras')]
        
        with engine.connect() as conn:
            # Verifica se a coluna descricao já existe
            if 'descricao' not in columns:
                conn.execute(text('ALTER TABLE quadras ADD COLUMN descricao TEXT'))
                print("Coluna 'descricao' adicionada com sucesso!")
                
            # Verifica se a coluna comodidades já existe
            if 'comodidades' not in columns:
                conn.execute(text('ALTER TABLE quadras ADD COLUMN comodidades TEXT'))
                print("Coluna 'comodidades' adicionada com sucesso!")
            
            conn.commit()
        
        print("Migração concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        
if __name__ == "__main__":
    run_migration()

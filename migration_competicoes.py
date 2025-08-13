from database import engine
from sqlalchemy import text, inspect
import models

def run_migration():
    print("Iniciando migração da tabela competicoes...")
    
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('competicoes')]
        
        with engine.connect() as conn:
            # Adicionar novas colunas que não existem
            if 'categoria' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN categoria VARCHAR(100)'))
                print("Coluna 'categoria' adicionada com sucesso!")
            
            if 'formato' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN formato VARCHAR(100)'))
                print("Coluna 'formato' adicionada com sucesso!")
                
            if 'minimo_participantes' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN minimo_participantes INTEGER'))
                print("Coluna 'minimo_participantes' adicionada com sucesso!")
                
            if 'permite_equipes' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN permite_equipes BOOLEAN DEFAULT FALSE'))
                print("Coluna 'permite_equipes' adicionada com sucesso!")
                
            if 'data_fim_inscricoes' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN data_fim_inscricoes DATETIME'))
                print("Coluna 'data_fim_inscricoes' adicionada com sucesso!")
                
            if 'quadra_id' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN quadra_id INTEGER REFERENCES quadras(id)'))
                print("Coluna 'quadra_id' adicionada com sucesso!")
                
            if 'requisitos' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN requisitos TEXT'))
                print("Coluna 'requisitos' adicionada com sucesso!")
            
            conn.commit()
        
        print("Migração da tabela competicoes concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        
if __name__ == "__main__":
    run_migration()

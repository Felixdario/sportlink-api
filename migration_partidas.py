from database import engine
from sqlalchemy import text, inspect
import models

def run_migration():
    print("Iniciando migração das tabelas de partidas e resultados...")
    
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        with engine.connect() as conn:
            # Criar tabela de equipes
            if 'equipes' not in tables:
                conn.execute(text('''
                CREATE TABLE equipes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(100) NOT NULL,
                    descricao TEXT,
                    logo VARCHAR(255),
                    competicao_id INTEGER,
                    capitao_id INTEGER,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (competicao_id) REFERENCES competicoes(id),
                    FOREIGN KEY (capitao_id) REFERENCES atletas(id)
                )
                '''))
                print("Tabela 'equipes' criada com sucesso!")
                
            # Criar tabela membro_equipe
            if 'membro_equipe' not in tables:
                conn.execute(text('''
                CREATE TABLE membro_equipe (
                    equipe_id INTEGER,
                    atleta_id INTEGER,
                    funcao VARCHAR(50) DEFAULT 'jogador',
                    status VARCHAR(20) DEFAULT 'ativo',
                    PRIMARY KEY (equipe_id, atleta_id),
                    FOREIGN KEY (equipe_id) REFERENCES equipes(id),
                    FOREIGN KEY (atleta_id) REFERENCES atletas(id)
                )
                '''))
                print("Tabela 'membro_equipe' criada com sucesso!")
                
            # Criar tabela de partidas
            if 'partidas' not in tables:
                conn.execute(text('''
                CREATE TABLE partidas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    competicao_id INTEGER,
                    fase VARCHAR(50),
                    data DATETIME,
                    local VARCHAR(255),
                    quadra_id INTEGER,
                    equipe1_id INTEGER,
                    equipe2_id INTEGER,
                    atleta1_id INTEGER,
                    atleta2_id INTEGER,
                    status VARCHAR(20) DEFAULT 'agendada',
                    resultado_equipe1 INTEGER,
                    resultado_equipe2 INTEGER,
                    detalhes TEXT,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (competicao_id) REFERENCES competicoes(id),
                    FOREIGN KEY (quadra_id) REFERENCES quadras(id),
                    FOREIGN KEY (equipe1_id) REFERENCES equipes(id),
                    FOREIGN KEY (equipe2_id) REFERENCES equipes(id),
                    FOREIGN KEY (atleta1_id) REFERENCES atletas(id),
                    FOREIGN KEY (atleta2_id) REFERENCES atletas(id)
                )
                '''))
                print("Tabela 'partidas' criada com sucesso!")
                
            # Criar tabela de eventos de partida
            if 'eventos_partida' not in tables:
                conn.execute(text('''
                CREATE TABLE eventos_partida (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    partida_id INTEGER,
                    tipo VARCHAR(50),
                    tempo VARCHAR(20),
                    descricao TEXT,
                    atleta_id INTEGER,
                    equipe_id INTEGER,
                    valor INTEGER,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partida_id) REFERENCES partidas(id),
                    FOREIGN KEY (atleta_id) REFERENCES atletas(id),
                    FOREIGN KEY (equipe_id) REFERENCES equipes(id)
                )
                '''))
                print("Tabela 'eventos_partida' criada com sucesso!")
                
            # Adicionar níveis à tabela de competições
            columns = [col['name'] for col in inspector.get_columns('competicoes')]
            if 'nivel_minimo' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN nivel_minimo VARCHAR(50)'))
                print("Coluna 'nivel_minimo' adicionada à tabela 'competicoes'!")
                
            if 'nivel_maximo' not in columns:
                conn.execute(text('ALTER TABLE competicoes ADD COLUMN nivel_maximo VARCHAR(50)'))
                print("Coluna 'nivel_maximo' adicionada à tabela 'competicoes'!")
                
            conn.commit()
        
        print("Migração concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        
if __name__ == "__main__":
    run_migration()

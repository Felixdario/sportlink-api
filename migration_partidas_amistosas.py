from database import engine
from sqlalchemy import text, inspect


def run_migration():
    print("Iniciando migração das tabelas de partidas amistosas...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        with engine.connect() as conn:
            # Criar tabela de partidas_amistosas
            if 'partidas_amistosas' not in tables:
                conn.execute(text('''
                CREATE TABLE partidas_amistosas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    esporte_id INTEGER,
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
                    organizador_id INTEGER,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (esporte_id) REFERENCES esportes(id),
                    FOREIGN KEY (quadra_id) REFERENCES quadras(id),
                    FOREIGN KEY (equipe1_id) REFERENCES equipes(id),
                    FOREIGN KEY (equipe2_id) REFERENCES equipes(id),
                    FOREIGN KEY (atleta1_id) REFERENCES atletas(id),
                    FOREIGN KEY (atleta2_id) REFERENCES atletas(id),
                    FOREIGN KEY (organizador_id) REFERENCES usuarios(id)
                )
                '''))
                print("Tabela 'partidas_amistosas' criada com sucesso!")

            # Criar tabela de eventos_partida_amistosa
            if 'eventos_partida_amistosa' not in tables:
                conn.execute(text('''
                CREATE TABLE eventos_partida_amistosa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    partida_id INTEGER,
                    tipo VARCHAR(50),
                    tempo VARCHAR(20),
                    descricao TEXT,
                    atleta_id INTEGER,
                    equipe_id INTEGER,
                    valor INTEGER,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (partida_id) REFERENCES partidas_amistosas(id),
                    FOREIGN KEY (atleta_id) REFERENCES atletas(id),
                    FOREIGN KEY (equipe_id) REFERENCES equipes(id)
                )
                '''))
                print("Tabela 'eventos_partida_amistosa' criada com sucesso!")

            conn.commit()

        print("Migração concluída com sucesso!")
    except Exception as e:
        print(f"Erro durante a migração: {e}")


if __name__ == "__main__":
    run_migration()

from fastapi import FastAPI
from database import Base, engine
from routers import (
    usuarios, atletas, esportes, quadras, competicoes,
    competicao_participantes, competicao_regras,
    conversas, mensagens, conquistas,
    quadra_avaliacoes, atividades
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Sportlink")

app.include_router(usuarios.router)
app.include_router(atletas.router)
app.include_router(esportes.router)
app.include_router(quadras.router)
app.include_router(competicoes.router)
app.include_router(competicao_participantes.router)
app.include_router(competicao_regras.router)
app.include_router(conversas.router)
app.include_router(mensagens.router)
app.include_router(conquistas.router)
app.include_router(quadra_avaliacoes.router)
app.include_router(atividades.router)

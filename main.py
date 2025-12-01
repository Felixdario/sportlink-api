from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import (
    usuarios, atletas, esportes, quadras, competicoes,
    competicao_participantes, competicao_regras,
    conquistas, quadra_avaliacoes, atividades,
    equipes, partidas
)
from routers import partidas_amistosas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Sportlink")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://sportlink-webapp.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(atletas.router)
app.include_router(esportes.router)
app.include_router(quadras.router)
app.include_router(competicoes.router)
app.include_router(competicao_participantes.router)
app.include_router(competicao_regras.router)
app.include_router(conquistas.router)
app.include_router(quadra_avaliacoes.router)
app.include_router(atividades.router)
app.include_router(equipes.router)
app.include_router(partidas.router)
app.include_router(partidas_amistosas.router)

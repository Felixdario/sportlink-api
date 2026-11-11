# API Sportlink

API desenvolvida em Python utilizando [FastAPI](https://fastapi.tiangolo.com/) para gerenciamento de usuários, atletas, quadras, esportes, competições, atividades, conquistas, conversas, mensagens e avaliações de quadras.

## Sumário

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Requisitos](#requisitos)
- [Configuração e Execução](#configuração-e-execução)
- [Endpoints Principais](#endpoints-principais)
- [Testes](#testes)
- [Dev Containers](#dev-containers)
- [Licença](#licença)

---

## Visão Geral

Este projeto fornece uma API RESTful para um sistema esportivo, permitindo cadastro e gerenciamento de usuários, perfis de atletas, quadras, esportes, competições, atividades, conquistas, conversas, mensagens e avaliações de quadras.

A documentação interativa da API pode ser acessada em `/docs` após iniciar o servidor.

---

## Funcionalidades

- Cadastro e autenticação de usuários
- Gerenciamento de perfis de atletas
- Cadastro e consulta de esportes
- Cadastro e consulta de quadras
- Gerenciamento de competições e inscrições
- Sistema de mensagens e conversas
- Ranking e conquistas de atletas
- Avaliações de quadras
- Agendamento de atividades

---

## Estrutura do Projeto

```
.
├── main.py                # Ponto de entrada da aplicação FastAPI
├── models.py              # Modelos ORM SQLAlchemy e Pydantic
├── database.py            # Configuração do banco de dados SQLite
├── getdb.py               # Dependência para obter sessão do banco
├── requirements.txt       # Dependências de produção
├── dev-requirements.txt   # Dependências de desenvolvimento
├── pyproject.toml         # Configuração do projeto Python
├── README.md              # Este arquivo
├── .gitignore
├── seguranca.py           # Hash de senha (scrypt)
├── migration_senhas.py    # Converte senhas antigas em texto puro para hash
├── tests/                 # Testes com pytest
├── routers/               # Módulos de rotas da API
│   ├── usuarios.py
│   ├── atletas.py
│   ├── esportes.py
│   ├── quadras.py
│   ├── competicoes.py
│   ├── competicao_participantes.py
│   ├── competicao_regras.py
│   ├── conversas.py
│   ├── mensagens.py
│   ├── conquistas.py
│   ├── quadra_avaliacoes.py
│   └── atividades.py
├── .devcontainer/         # Configuração para Dev Containers
│   └── devcontainer.json
└── .vscode/               # Configurações do VS Code
    ├── launch.json
    └── settings.json
```

---

## Requisitos

- Python >= 3.11
- [Docker](https://www.docker.com/products/docker-desktop) (opcional, recomendado para Dev Containers)
- [VS Code](https://code.visualstudio.com/) com extensões recomendadas:
  - Dev Containers
  - Python
  - Python Debugger
  - Pylance

---

## Configuração e Execução

1. **Clone o repositório:**

   ```sh
   git clone <url-do-repositorio>
   cd fastapi-template
   ```

2. **(Opcional) Abra no VS Code e use Dev Container:**

   - Abra a pasta no VS Code.
   - Execute o comando **Dev Container: Reabrir no Container** na paleta de comandos.

3. **Instale as dependências:**

   ```sh
   pip install -r dev-requirements.txt
   ```

4. **Banco de dados:** a API cria o SQLite `sportlink.db` na primeira execução (ou usa `DATABASE_URL`). O arquivo não é versionado. Se você tem um banco criado antes do hash de senha, rode uma vez:

   ```sh
   python migration_senhas.py
   ```

5. **Execute a aplicação:**

   ```sh
   uvicorn main:app --reload --port 5000
   ```

6. **Acesse a documentação interativa:**
   - [http://localhost:5000/docs](http://localhost:5000/docs)

---

## Endpoints Principais

A API está organizada em múltiplos módulos de rotas, cada um responsável por um recurso:

- `/usuarios` - Cadastro e listagem de usuários
- `/atletas` - Gerenciamento de perfis de atletas
- `/esportes` - Cadastro e consulta de esportes
- `/quadras` - Cadastro e consulta de quadras
- `/competicoes` - Gerenciamento de competições
- `/competicao_participantes` - Inscrição de atletas em competições
- `/competicao_regras` - Regras de competições
- `/conversas` - Criação e listagem de conversas
- `/mensagens` - Envio e listagem de mensagens
- `/conquistas` - Cadastro e consulta de conquistas
- `/quadra_avaliacoes` - Avaliação de quadras
- `/atividades` - Agendamento e participação em atividades

Consulte `/docs` para detalhes de cada endpoint, parâmetros e exemplos de uso.

---

## Testes

- As senhas são gravadas com hash scrypt (`seguranca.py`), nunca em texto puro. Senhas antigas em texto puro viram hash no primeiro login certo ou com `migration_senhas.py`.
- Os testes usam `pytest` e um SQLite temporário, sem tocar no `sportlink.db`:
  ```sh
  pytest
  ```

---

## Dev Containers

O projeto está pronto para uso com [Dev Containers](https://containers.dev/). Basta abrir no VS Code e reabrir no container para um ambiente de desenvolvimento isolado e pronto para uso.

---

## Licença

Este projeto é fornecido sem garantia e para fins educacionais. Adapte conforme necessário para seu uso.

---

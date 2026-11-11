import os
import sys
import tempfile
from pathlib import Path

# Banco SQLite temporário: definido antes de importar `database`, que lê DATABASE_URL na importação.
_pasta = tempfile.mkdtemp(prefix="sportlink-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_pasta, 'teste.db').as_posix()}"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

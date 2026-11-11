"""Hash de senha com scrypt, da biblioteca padrão do Python.

Formato gravado em `usuarios.senha_hash`:

    scrypt$<n>$<r>$<p>$<sal em base64>$<hash em base64>

Senhas gravadas antes desta mudança (texto puro) ainda são aceitas uma vez: `verificar_senha`
compara em tempo constante e avisa que o valor precisa ser regravado com hash.
"""

import base64
import hashlib
import hmac
import secrets

PREFIXO = "scrypt"
N, R, P = 2**14, 8, 1  # ~16 MB de memória por hash; parâmetros recomendados para logins interativos
TAMANHO_SAL = 16
TAMANHO_HASH = 32


def _derivar(senha: str, sal: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(
        senha.encode("utf-8"), salt=sal, n=n, r=r, p=p, dklen=TAMANHO_HASH, maxmem=64 * 1024 * 1024
    )


def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(TAMANHO_SAL)
    derivado = _derivar(senha, sal, N, R, P)
    return "$".join(
        [
            PREFIXO,
            str(N),
            str(R),
            str(P),
            base64.b64encode(sal).decode("ascii"),
            base64.b64encode(derivado).decode("ascii"),
        ]
    )


def eh_hash(valor: str) -> bool:
    return valor.startswith(PREFIXO + "$") and valor.count("$") == 5


def verificar_senha(senha: str, armazenado: str) -> tuple[bool, bool]:
    """Devolve (confere, precisa_regravar).

    `precisa_regravar` é True quando o valor armazenado ainda é texto puro (legado) e a senha
    conferiu: quem chama deve gravar `gerar_hash(senha)` no lugar.
    """
    if eh_hash(armazenado):
        try:
            _, n, r, p, sal_b64, hash_b64 = armazenado.split("$")
            esperado = base64.b64decode(hash_b64)
            calculado = _derivar(senha, base64.b64decode(sal_b64), int(n), int(r), int(p))
        except (ValueError, TypeError):
            return False, False
        return hmac.compare_digest(calculado, esperado), False

    confere = hmac.compare_digest(senha.encode("utf-8"), armazenado.encode("utf-8"))
    return confere, confere


# Hash de uma senha qualquer, usado quando o e-mail não existe: o login leva o mesmo tempo nos
# dois casos e não revela quais e-mails estão cadastrados.
HASH_FICTICIO = gerar_hash(secrets.token_urlsafe(16))

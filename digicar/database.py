"""Configuracao de um a quatro bancos relacionais Django."""
from pathlib import Path
from typing import Mapping


_ENGINES = {
    "sqlite": "django.db.backends.sqlite3",
    "mysql": "django.db.backends.mysql",
    "postgresql": "django.db.backends.postgresql",
    "postgres": "django.db.backends.postgresql",
}


def _configurar(environ: Mapping[str, str], base_dir: Path, prefix: str, *, principal=False) -> dict:
    engine_key = f"{prefix}ENGINE"
    if principal:
        engine = environ.get(engine_key, "mysql" if environ.get("DB_HOST") else "sqlite").lower()
    else:
        engine = environ.get(engine_key, "").lower()
    if not engine:
        raise ValueError(f"{engine_key} é obrigatório para configurar esse banco")
    if engine not in _ENGINES:
        raise ValueError(f"{engine_key} inválido. Use: {', '.join(_ENGINES)}")

    config = {"ENGINE": _ENGINES[engine]}
    if engine == "sqlite":
        config["NAME"] = environ.get(f"{prefix}NAME", str(base_dir / ("db.sqlite3" if principal else f"db_{prefix.lower().rstrip('_')}.sqlite3")))
        return config

    config.update({
        "NAME": environ.get(f"{prefix}NAME", "digicar"),
        "USER": environ.get(f"{prefix}USER", ""),
        "PASSWORD": environ.get(f"{prefix}PASSWORD", ""),
        "HOST": environ.get(f"{prefix}HOST", "localhost"),
        "PORT": environ.get(f"{prefix}PORT", "3306" if engine == "mysql" else "5432"),
    })
    if engine == "mysql":
        config["OPTIONS"] = {"init_command": "SET sql_mode='STRICT_TRANS_TABLES'", "charset": "utf8mb4"}
    return config


def criar_configuracao_bancos(environ: Mapping[str, str], base_dir: Path) -> dict[str, dict]:
    """Cria default e aliases db2/db3/db4 opcionais via DB_2_*, DB_3_*, DB_4_*.

    O banco default preserva a configuracao legada DB_*.
    """
    databases = {"default": _configurar(environ, base_dir, "DB_", principal=True)}
    for numero, alias in ((2, "db2"), (3, "db3"), (4, "db4")):
        prefix = f"DB_{numero}_"
        if environ.get(prefix + "ENGINE"):
            databases[alias] = _configurar(environ, base_dir, prefix)
    return databases

from pathlib import Path
from typing import Mapping


def criar_configuracao_bancos(
    environ: Mapping[str, str], base_dir: Path
) -> dict[str, dict]:
    engine = environ.get("DB_ENGINE", "mysql" if environ.get("DB_HOST") else "sqlite")
    engine = engine.lower()

    if engine == "sqlite":
        nome = environ.get("DB_NAME", str(base_dir / "db.sqlite3"))
        return {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": nome,
            }
        }

    engines = {
        "mysql": "django.db.backends.mysql",
        "postgresql": "django.db.backends.postgresql",
        "postgres": "django.db.backends.postgresql",
    }
    if engine not in engines:
        suportados = ", ".join(sorted(set(engines) | {"sqlite"}))
        raise ValueError(f"DB_ENGINE inválido. Use um destes valores: {suportados}")

    configuracao = {
        "ENGINE": engines[engine],
        "NAME": environ.get("DB_NAME", "digicar"),
        "USER": environ.get("DB_USER", ""),
        "PASSWORD": environ.get("DB_PASSWORD", ""),
        "HOST": environ.get("DB_HOST", "localhost"),
        "PORT": environ.get("DB_PORT", "3306" if engine == "mysql" else "5432"),
    }
    if engine == "mysql":
        configuracao["OPTIONS"] = {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "charset": "utf8mb4",
        }

    return {"default": configuracao}

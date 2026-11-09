# Versão do sistema (versionamento semântico: MAJOR.MINOR.PATCH).
#   MAJOR: mudança incompatível · MINOR: funcionalidade nova · PATCH: correção
__version__ = "1.1.0"

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    # O projeto usa SQLite por padrão; PyMySQL só é necessário com MySQL.
    pass

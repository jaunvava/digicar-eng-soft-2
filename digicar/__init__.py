try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    # O projeto usa SQLite por padrão; PyMySQL só é necessário com MySQL.
    pass

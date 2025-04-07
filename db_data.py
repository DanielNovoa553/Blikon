import psycopg2

def connectdb():
    try:
        return psycopg2.connect(
            dbname="blikon_db",
            user="postgres",
            password="Inicio01",
            host="localhost",
            port="5432"
        )
    except Exception as e:
        print(f'Error al conectar a la base de datos: {e}')
        return False
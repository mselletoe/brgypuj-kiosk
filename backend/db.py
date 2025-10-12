import psycopg2

DB_URL = "postgresql://admin:admin7890@localhost:5432/kioskdb"

def get_conn():
    return psycopg2.connect(DB_URL)
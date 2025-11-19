import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@citus-coordinator:5432/historias")

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def fetch_paciente(documento_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM paciente WHERE documento_id = %s;", (documento_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

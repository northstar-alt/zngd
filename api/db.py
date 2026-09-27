import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Open a new connection to the prototype database using .env settings."""
    return psycopg.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DBNAME", "prototype"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", ""),
        row_factory=dict_row,
    )

def get_all_species(conn):
    """Return every row in the species table."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM species ORDER_BY species_id;")
        return cur.fetchall()

def get_get_species_by_id(conn, species_id):
    """Return a single row from the species table by species_id (one row or None of it doesn't exist)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM species WHERE species_id = %s;",
              (species_id,),
              )
        return cur.fetchone()

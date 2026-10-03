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
        cur.execute("SELECT * FROM species ORDER BY species_id;")
        return cur.fetchall()

def get_species_by_id(conn, species_id):
    """Return a single row from the species table by species_id (one row or None if it doesn't exist)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM species WHERE species_id = %s;",
              (species_id,),
              )
        return cur.fetchone()

def get_all_pathogens(conn):
    """Return every row in the pathogens table."""
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM pathogen ORDER BY pathogen_id;")
        return cur.fetchall()

def get_pathogen_by_id(conn, pathogen_id):
    """Return a single row from the pathogens table by pathogen_id (one row or None if it doesn't exist)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM pathogen WHERE pathogen_id = %s;",
              (pathogen_id,),
              )
        return cur.fetchone()

def get_all_organisms(conn):
    """Return every organism, joined with its species and pathogen information."""
    query = """
        SELECT 
            o.organism_id,
            s.scientific_name AS species_name,
            p.scientific_name AS pathogen_name,
            o.collection_date,
            o.specimen_type,
            o.host_status,
            o.notes
        FROM organism o
        JOIN species s ON o.species_id = s.species_id
        LEFT JOIN pathogen p ON o.pathogen_id = p.pathogen_id
        ORDER BY o.organism_id;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def get_organism_by_id(conn, organism_id):
    """Return a single organism ID, joined with its species and pathogen information"""
    query = """
        SELECT 
            o.organism_id,
            s.scientific_name AS species_name,
            p.scientific_name AS pathogen_name,
            o.collection_date,
            o.specimen_type,
            o.host_status,
            o.notes
        FROM organism o
        JOIN species s ON o.species_id = s.species_id
        LEFT JOIN pathogen p ON o.pathogen_id = p.pathogen_id
        WHERE o.organism_id = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (organism_id,))
        return cur.fetchone()

def get_all_sequences(conn):
    """Return a summary of every sequence, with no raw sequence data"""
    query = """
        SELECT 
            sequence_id,
            organism_id,
            ncbi_accession,
            sequence_type,
            sequence_length,
            gc_content,
            retrieved_at
        FROM sequence
        ORDER BY sequence_id;
    """
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

def get_sequence_by_id(conn, sequence_id):
    """Return full detail for a single sequence plus a raw sequence and the annotations."""
    query = """
        SELECT *
        FROM sequence
        WHERE sequence_id = %s;
    """
    with conn.cursor() as cur:
        cur.execute(query, (sequence_id,))
        return cur.fetchone()
    
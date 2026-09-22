import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Open a new connection to the prototype database"""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        dbname=os.getenv("PG_DBNAME", "prototype"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", ""),
    )
    
    
def fetch_organism_targets(conn):
    """
    Return one row per organism, joined with its species and pathogen names,
    so the ingestion script knows what to search NCBI for.
    
    Only returns organims that have a pathogen_id set (host_status = 'infected' or 'suspected').
    """
    
    query = """
        SELECT 
            o.organism_id,
            s.scientific_name AS species_name,
            p.scientific_name AS pathogen_name,
            p.ncbi_taxon_id AS pathogen_taxon_id
        FROM organism o
        JOIN species s ON o.species_id = s.species_id
        JOIN pathogen p ON o.pathogen_id = p.pathogen_id
        WHERE o.pathogen_id IS NOT NULL
        ORDER BY o.organism_id;
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query)
        return cur.fetchall()
        
        
def sequence_exists(conn, ncbi_accession):
    """Check whether this accession has already been ingested, we wanna avoid duplication."""
    with conn.cursor() as cur:
        cur.execute(
        "SELECT 1 FROM sequence WHERE ncbi_accession = %s;",
        (ncbi_accession,),
        )
        return cur.fetchone() is not None
        
        
def insert_sequence(conn, organism_id, ncbi_accession, sequence_type, sequence_length, gc_content, raw_sequence, annotations, retrieved_at):
    """Insert one fetched NCBI record into the sequence table"""
    query="""
        INSERT INTO sequence (
            organism_id, ncbi_accession, sequence_type, sequence_length, gc_content, raw_sequence, annotations, retrieved_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING sequence_id;
    """
    with conn.cursor() as cur:
        cur.execute(query, (
            organism_id,
            ncbi_accession,
            sequence_type,
            sequence_length,
            gc_content,
            raw_sequence,
            json.dumps(annotations),
            retrieved_at,
        ))
        sequence_id = cur.fetchone()[0]
    conn.commit()
    return sequence_id
            
            
def log_audit(conn, table_name, record_id, action, changed_by, new_data):
    """Write a row to audit_log for any insert performed"""
    query = """
        INSERT INTO audit_log (table_name, record_id, action, changed_by, new_data)
        VALUES (%s, %s, %s, %s, %s);
    """
    with conn.cursor() as cur:
        cur.execute(query, (
        table_name,
        record_id,
        action,
        changed_by,
        json.dumps(new_data),
    ))
    conn.commit()
    
    
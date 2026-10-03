from fastapi import FastAPI, HTTPException
import db

app = FastAPI(
    title = "ZNGD API",
    description = "Read-only API for the Zimbabwe genomic curation prototype.",
    version = "0.1.0",
)


@app.get("/")
def root():
    """Simple health check that confirms the API is running."""
    return {"message": "ZNGD API is running."}


@app.get("/species")
def list_species():
    """Return every species in the database."""
    conn = db.get_connection()
    try:
        return db.get_all_species(conn)
    finally:
        conn.close()


@app.get("/species/{species_id}")
def get_species(species_id: int):
    """Return one species by its species_id."""
    conn = db.get_connection()
    try:
        species = db.get_species_by_id(conn, species_id)
        if species is None:
            raise HTTPException(status_code=404, detail="Species not found")
        return species
    finally:
        conn.close()


@app.get("/pathogens")
def list_pathogens():
    """Return every pathogen in the database."""
    conn = db.get_connection()
    try:
        return db.get_all_pathogens(conn)
    finally:
        conn.close()


@app.get("/pathogens/{pathogen_id}")
def get_pathogen(pathogen_id: int):
    """Return one pathogen by its pathogen_id."""
    conn = db.get_connection()
    try:
        pathogen = db.get_pathogen_by_id(conn, pathogen_id)
        if pathogen is None:
            raise HTTPException(status_code=404, detail="Pathogen not found")
        return pathogen
    finally:
        conn.close()


@app.get("/organisms")
def list_organisms():
    """Return every organism, with readable species and pathogen information."""
    conn = db.get_connection()
    try:
        return db.get_all_organisms(conn)
    finally:
        conn.close()


@app.get("/organisms/{organism_id}")
def get_organism(organism_id: int):
    """Return one organism by its organism_id, with readable species and pathogen information."""
    conn = db.get_connection()
    try:
        organism = db.get_organism_by_id(conn, organism_id)
        if organism is None:
            raise HTTPException(status_code=404, detail="Organism not found")
        return organism
    finally:
        conn.close()


@app.get("/sequences")
def list_sequences():
    """Return a lightweight summary of every sequence (no raw sequence data)."""
    conn = db.get_connection()
    try:
        return db.get_all_sequences(conn)
    finally:
        conn.close()


@app.get("/sequences/{sequence_id}")
def get_sequence(sequence_id: int):
    """Return full detail for one sequence, including the raw sequence and annotations."""
    conn = db.get_connection()
    try:
        sequence = db.get_sequence_by_id(conn, sequence_id)
        if sequence is None:
            raise HTTPException(status_code=404, detail="Sequence not found")
        return sequence
    finally:
        conn.close()
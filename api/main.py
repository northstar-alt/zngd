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

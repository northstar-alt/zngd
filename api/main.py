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
def list_organisms(host_status: str = None, species_name: str = None, pathogen_name: str = None):
    """Return every organism, with readable species and pathogen information. Optionally filter by host_status, species_name, and/or pathogen_name."""
    conn = db.get_connection()
    try:
        return db.get_all_organisms(conn, host_status, species_name, pathogen_name)
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



@app.get("/collection_site")
def list_collection_sites():
    """Return every collection site in the database."""
    conn = db.get_connection()
    try:
        return db.get_all_collection_sites(conn)
    finally:
        conn.close()


@app.get("/collection_site/{site_id}")
def get_collection_site(site_id: int):
    """Return one collection site by its site_id."""
    conn = db.get_connection()
    try:
        site = db.get_collection_site_by_id(conn, site_id)
        if site is None:
            raise HTTPException(status_code=404, detail="Collection site not found")
        return site
    finally:
        conn.close()


@app.get("/qc")
def list_qc_metrics():
    """Return every row in the qc table in the database."""
    conn = db.get_connection()
    try:
        return db.get_all_qc_metrics(conn)
    finally:
        conn.close()


@app.get("/qc/{qc_id}")
def get_qc_metric(qc_id: int):
    """Return one row from the qc table by qc_id."""
    conn = db.get_connection()
    try:
        qc_metric = db.get_qc_metrics_by_id(conn, qc_id)
        if qc_metric is None:
            raise HTTPException(status_code=404, detail="QC metric not found")
        return qc_metric
    finally:
        conn.close()
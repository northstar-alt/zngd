# ZNGD Prototype (Zimbabwe National Genomic Database)

A domain-specific relational database and automated bio-data pipeline designed to curate, store, and analyze genomic sequences of agricultural pathogens affecting livestock and crops in Zimbabwe.

This project combines a normalized **PostgreSQL** relational schema, an automated **Python ETL pipeline** (utilizing `psycopg3`, BioPython, and the NCBI Entrez API), and an **R analytics suite (`ggplot2`)** for exploratory sequence analysis.

---

## Key Features

- **Host & Pathogen Tracking:** Models agricultural livestock and plant hosts, disease-causing pathogens (viruses, bacteria, fungi), and geographic sampling locations across Zimbabwe.
- **Automated NCBI Ingestion Pipeline:** Queries the NCBI Entrez Nucleotide database, fetches GenBank sequence records, dynamically parses JSON annotations, computes GC content percentage, and logs metadata.
- **Audit Logging & QC:** Implements automated transaction tracking (`audit_log`) for data lineage and built-in table structures for quality control (`qc`) workflows.
- **Duplicate Prevention & API Throttling:** Ensures accession uniqueness (`ncbi_accession`) and dynamically adjusts request rates based on NCBI API key presence.
- **Visual Analytics (R):** Includes R scripts to query PostgreSQL directly and render charts (`ggplot2`) analyzing sequence counts, GC content distributions, and log-scaled sequence lengths.

---

## Tech Stack & Dependencies

- **Database:** PostgreSQL (with `JSONB` indexing for flexible feature annotations)
- **Data Ingestion & ETL (Python):**
  - `psycopg` (v3) — PostgreSQL driver
  - `BioPython` (`Entrez`, `SeqIO`, `gc_fraction`) — GenBank parsing & sequence utility
  - `python-dotenv` — Environment configuration management
  - `argparse` — Command-line interface orchestration
- **Data Analytics & Visualization (R):**
  - `DBI` & `RPostgres` — Direct relational database querying
  - `dplyr` & `ggplot2` — Data manipulation and visualization

---

## Database Architecture Highlights

The PostgreSQL schema (`zngd_schema.sql`) uses a normalized structure:

1. **`species` & `pathogen`**: Reference tables for hosts (livestock/plants) and infectious pathogens.
2. **`collection_site`**: Geographic locations tracking district, province, and coordinates.
3. **`organism`**: Specimen records linking host, pathogen, collection site, and contributor.
4. **`sequence`**: Genomic sequence records containing raw FASTA sequences, length, GC percentage, and `JSONB` feature annotations.
5. **`audit_log`**: Generic change-tracking table capturing `insert`, `update`, and `delete` events as JSON objects.

---

## Getting Started

### 1. Prerequisites
- **PostgreSQL** (v14 or higher)
- **Python 3.9+**
- **R & RStudio** (optional, for visualization)

### 2. Environment Setup
Create a `.env` file in the project root with your database credentials and NCBI API details:

```env
# PostgreSQL Configuration
PG_HOST=localhost
PG_PORT=5432
PG_DBNAME=prototype
PG_USER=postgres
PG_PASSWORD=your_password_here

# NCBI Entrez Credentials
NCBI_EMAIL=your_email@example.com
NCBI_API_KEY=your_ncbi_api_key_here


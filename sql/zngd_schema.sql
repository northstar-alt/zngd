-- =====================================================================
-- ZNGD Prototype Schema
-- Zimbabwe-focused genomic curation database (livestock & plant hosts,
-- their pathogens, and NCBI-sourced sequence data)
-- Target: PostgreSQL 18
-- Run this while connected to the `prototype` database (\c prototype)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. species — host organisms (livestock, plants) tracked by ZNGD
-- ---------------------------------------------------------------------
CREATE TABLE species (
    species_id      BIGSERIAL PRIMARY KEY,
    scientific_name VARCHAR(100) NOT NULL,
    common_name     VARCHAR(100),
    category        VARCHAR(50) NOT NULL
                        CHECK (category IN ('livestock', 'plant', 'other')),
    ncbi_taxon_id   INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (scientific_name)
);

-- ---------------------------------------------------------------------
-- 2. pathogen — disease-causing agents (viruses, bacteria, fungi, etc.)
-- ---------------------------------------------------------------------
CREATE TABLE pathogen (
    pathogen_id     BIGSERIAL PRIMARY KEY,
    scientific_name VARCHAR(100) NOT NULL,
    common_name     VARCHAR(100),
    pathogen_type   VARCHAR(50) NOT NULL
                        CHECK (pathogen_type IN
                            ('virus', 'bacteria', 'fungus', 'parasite', 'protozoa', 'other')),
    ncbi_taxon_id   INTEGER,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (scientific_name)
);

-- ---------------------------------------------------------------------
-- 3. collection_site — where a specimen was collected in Zimbabwe
-- ---------------------------------------------------------------------
CREATE TABLE collection_site (
    site_id     BIGSERIAL PRIMARY KEY,
    site_name   VARCHAR(100),
    district    VARCHAR(100),
    province    VARCHAR(100),
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    site_type   VARCHAR(50),  -- e.g. farm, field station, abattoir, herbarium
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 4. contributor — researchers/students who curate or submit data
-- ---------------------------------------------------------------------
CREATE TABLE contributor (
    contributor_id  BIGSERIAL PRIMARY KEY,
    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) UNIQUE,
    affiliation     VARCHAR(200),
    orcid           VARCHAR(30),
    role            VARCHAR(50) DEFAULT 'researcher'
                        CHECK (role IN ('researcher', 'student', 'admin', 'collaborator')),
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------
-- 5. organism — an individual specimen/isolate record
-- ---------------------------------------------------------------------
CREATE TABLE organism (
    organism_id     BIGSERIAL PRIMARY KEY,
    species_id      BIGINT NOT NULL REFERENCES species(species_id),
    pathogen_id     BIGINT REFERENCES pathogen(pathogen_id),  -- nullable: not every organism is infected
    site_id         BIGINT REFERENCES collection_site(site_id),
    collected_by    BIGINT REFERENCES contributor(contributor_id),
    collection_date DATE,
    specimen_type   VARCHAR(50),  -- e.g. blood, tissue, leaf, swab
    host_status     VARCHAR(50)
                        CHECK (host_status IN ('healthy', 'infected', 'suspected', 'unknown')),
    notes           VARCHAR(300),
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_organism_species  ON organism(species_id);
CREATE INDEX idx_organism_pathogen ON organism(pathogen_id);
CREATE INDEX idx_organism_site     ON organism(site_id);

-- ---------------------------------------------------------------------
-- 6. sequence — genomic sequence data (pulled from NCBI via BioPython)
--    Annotations live here as JSONB rather than a separate table.
-- ---------------------------------------------------------------------
CREATE TABLE sequence (
    sequence_id     BIGSERIAL PRIMARY KEY,
    organism_id     BIGINT NOT NULL REFERENCES organism(organism_id),
    ncbi_accession  VARCHAR(30) UNIQUE,
    sequence_type   VARCHAR(50),  -- e.g. whole genome, gene fragment, 16S rRNA
    sequence_length INTEGER,
    gc_content      NUMERIC(5,2),
    raw_sequence    TEXT,         -- or a file path/reference for large sequences
    annotations     JSONB,        -- flexible feature data: gene names, positions, products
    retrieved_at    TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_sequence_organism ON sequence(organism_id);
CREATE INDEX idx_sequence_annotations ON sequence USING GIN (annotations);

-- ---------------------------------------------------------------------
-- 7. submission — tracks submitting/curating a sequence record
-- ---------------------------------------------------------------------
CREATE TABLE submission (
    submission_id       BIGSERIAL PRIMARY KEY,
    sequence_id         BIGINT NOT NULL REFERENCES sequence(sequence_id),
    contributor_id      BIGINT NOT NULL REFERENCES contributor(contributor_id),
    submission_status   VARCHAR(50) NOT NULL DEFAULT 'draft'
                            CHECK (submission_status IN ('draft', 'submitted', 'published', 'rejected')),
    ncbi_submission_id  VARCHAR(50),
    submitted_at        TIMESTAMP,
    notes                VARCHAR(300),
    created_at           TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_submission_sequence    ON submission(sequence_id);
CREATE INDEX idx_submission_contributor ON submission(contributor_id);

-- ---------------------------------------------------------------------
-- 8. qc — quality control checks on a sequence
-- ---------------------------------------------------------------------
CREATE TABLE qc (
    qc_id               BIGSERIAL PRIMARY KEY,
    sequence_id         BIGINT NOT NULL REFERENCES sequence(sequence_id),
    reviewed_by         BIGINT REFERENCES contributor(contributor_id),
    coverage            NUMERIC(6,2),
    contamination_flag  BOOLEAN DEFAULT FALSE,
    qc_status           VARCHAR(50) DEFAULT 'pending'
                            CHECK (qc_status IN ('pass', 'fail', 'pending')),
    qc_notes            VARCHAR(300),
    reviewed_at          TIMESTAMP
);

CREATE INDEX idx_qc_sequence ON qc(sequence_id);

-- ---------------------------------------------------------------------
-- 9. audit_log — generic change tracking across the schema
-- ---------------------------------------------------------------------
CREATE TABLE audit_log (
    audit_id    BIGSERIAL PRIMARY KEY,
    table_name  VARCHAR(50) NOT NULL,
    record_id   BIGINT NOT NULL,
    action      VARCHAR(20) NOT NULL
                    CHECK (action IN ('insert', 'update', 'delete')),
    changed_by  VARCHAR(100),
    old_data    JSONB,
    new_data    JSONB,
    changed_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_table_record ON audit_log(table_name, record_id);

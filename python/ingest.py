import argparse
import sys

import db
import ncbi_client

CHANGED_BY = "ingest.py (automated NCBI pull)"


def run(retmax):
    conn = db.get_connection()
    print("Connected to prototype database.")

    targets = db.fetch_organism_targets(conn)
    if not targets:
        print(
            "No organisms with pathogen linked were found. "
            "Seed the organism table first"
        )
        return

    seen_pairs = {}
    for row in targets:
        pair_key = (row["species_name"], row["pathogen_name"])
        seen_pairs.setdefault(pair_key, []).append(row["organism_id"])

    total_inserted = 0

    for (species_name, pathogen_name), organism_ids in seen_pairs.items():
        print(f"\nSearching NCBI for pathogen '{pathogen_name}' (host: '{species_name}')...")
        try:
            id_list = ncbi_client.search_pathogen_sequences(pathogen_name, retmax=retmax)
        except Exception as e:
            print(f"ERROR searching NCBI for pathogen '{pathogen_name}': {e}")
            continue

        if not id_list:
            print(f"No NCBI sequences found for pathogen '{pathogen_name}'")
            continue

        try:
            records = ncbi_client.fetch_sequence_records(id_list)
        except Exception as e:
            print(f"ERROR fetching NCBI sequence records for pathogen '{pathogen_name}': {e}")
            continue

        print(f"Fetched {len(records)} record(s). Inserting new ones...")

        for record in records:
            if db.sequence_exists(conn, record["ncbi_accession"]):
                print(
                    f"    Skipping {record['ncbi_accession']} already exists "
                    "in the database. Skipping."
                )
                continue

            organism_id = organism_ids[0]  # Use the first organism_id for this species-pathogen pair

            sequence_id = db.insert_sequence(
                conn,
                organism_id=organism_id,
                ncbi_accession=record["ncbi_accession"],
                sequence_type=record["sequence_type"],
                sequence_length=record["sequence_length"],
                gc_content=record["gc_content"],
                raw_sequence=record["raw_sequence"],
                annotations=record["annotations"],
                retrieved_at=record.get("retrieved_at"),
            )
            db.log_audit(
                conn,
                "sequence",
                sequence_id,
                "insert",
                CHANGED_BY,
                {
                    "ncbi_accession": record["ncbi_accession"],
                    "organism_id": organism_id,
                },
            )
            print(
                f"    Inserted {record['ncbi_accession']}"
                f"({record['sequence_length']} bp) -> sequence_id {sequence_id}"
            )
            total_inserted += 1

    print(f"Completed ingestion. Inserted {total_inserted} new sequence(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest pathogen sequence records from NCBI.")
    parser.add_argument("--retmax", type=int, default=10, help="Maximum number of NCBI sequence IDs to fetch per pathogen.")
    args = parser.parse_args()

    try:
        run(args.retmax)
    except Exception as exc:
        print(f"Fatal error during ingestion: {exc}", file=sys.stderr)
        raise

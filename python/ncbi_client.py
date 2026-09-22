import os
import time
from datetime import datetime, timezone
from Bio import Entrez, SeqIO
from Bio.SeqUtils import gc_fraction
from dotenv import load_dotenv

load_dotenv()
Entrez.email = os.getenv("NCBI_EMAIL")
_api_key = os.getenv("NCBI_API_KEY")
if _api_key:
    Entrez.api_key = _api_key

_REQUEST_DELAY = 0.11  if _api_key else 0.34  # seconds between requests, to avoid NCBI throttling

def search_pathogen_sequences(pathogen_name, retmax=5):
    """
    Search the nucleotide database for pathogens by name. Returns a list of NCBI accession numbers.
    """
    handle = Entrez.esearch(
        db="nucleotide", 
        term=f"{pathogen_name}[Organism] AND 100:250000[SLEN] NOT pdb[filter] NOT patent[filter]",  # filter out protein sequences and strict patents
        retmax=retmax,
        sort="relevance",
    )
    record = Entrez.read(handle)
    handle.close()
    time.sleep(_REQUEST_DELAY)
    return record.get("IdList", [])

def fetch_sequence_records(id_list):
    """
    Given a list of NCBI UIDs, fetch full GenBank records and parse them
    with SeqIO. Returns a list of dicts ready for db.insert_sequence().
    """
    if not id_list:
        return []

    handle = Entrez.efetch(
        db="nucleotide",
        id=id_list,
        rettype="gb",
        retmode="text",
    )
    results = []
    for seq_record in SeqIO.parse(handle, "genbank"):
        results.append(_parse_seq_record(seq_record))
    handle.close()
    time.sleep(_REQUEST_DELAY)
    return results

def _parse_seq_record(seq_record):
    """
    Converting a single BioPython SeqRecord into sequence table shape
    """
    sequence_str = str(seq_record.seq)
    gc_content = round(gc_fraction(seq_record.seq) * 100, 2) if len(seq_record.seq) > 0 else None  # convert to percentage

    annotations = []
    for feature in seq_record.features:
            annotations.append({
            "type": feature.type,
            "location": str(feature.location),
            "qualifiers": {
                k: (v if isinstance(v, list) else [v])
                for k, v in feature.qualifiers.items()
    },
    })

    molecule_type = seq_record.annotations.get("molecule_type", "unknown")
    description = seq_record.description or""

    return {
        "ncbi_accession": seq_record.id,
        "sequence_type": molecule_type,
        "sequence_length": len(seq_record.seq),
        "gc_content": gc_content,
        "raw_sequence": sequence_str,
        "annotations": {
             "description": description,
             "features": annotations,
        },
        "retrieved_at": datetime.now(timezone.utc)
    }
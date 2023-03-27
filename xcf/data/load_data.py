"""Functionality for downloading PDB report using provided search and report jsons and saving it to SQL database.

Class PDBEndpoint contains info on PDB enpoints for search and report GET requests. Has to be updated when they change.

Function search_PDB takes a json file containing properly formatted PDB search query and outputs a list of PDB IDs of entries matching the query.

Function report_from_PDB  takes the IDs list from search_PDB, a json file containing properly formatted PDB report query, and optional batch size. 
It downloads and outputs a pandas DataFrame containing the requested PDB report.
Unfortunetaly the schema for converting raw PDB report to DataFrame changes with every report query and has to be coded manually in _json_to_dataframe private function.

Function save_raw_data_to_db takes the DataFrame and saves it to a PostgreSQL database configured in xcf.data.db module. Schema has to match the one defined in _json_to_dataframe.

TDB: Modular interface for DataFrame and SQL schemas.

Typical usage example:

ids_list = xcf.search_PDB(search_json)
data_raw = xcf.report_from_PDB(ids_list, report_json, batch_size=5000)
save_raw_data_to_db(data_raw)
"""

import requests
import pandas as pd
from datetime import date
from sqlalchemy.types import Float, Text, String
from .db import create_db_connection

# define PDB endpoints
class PDBEndpoint:
    _search = "https://search.rcsb.org/rcsbsearch/v2/query"
    _report = "https://data.rcsb.org/graphql"

    @classmethod
    def search(cls):
        return cls._search

    @classmethod
    def report(cls):
        return cls._report


# Search PDB for list of entry IDs
def _get_ids_list(search_query):
    search_response = requests.get(
        url=PDBEndpoint.search(), params={"json": search_query}
    )
    result_set = search_response.json()["result_set"]
    ids_list = []
    for item in result_set:
        id = item["identifier"]
        add_quotes = f'"{id}"'
        ids_list.append(add_quotes)
    return ids_list


# Build a list of report queries to be sent in batches, too large batch size can be denied by the PDB server
def _build_report_query(ids_list, report_query_empty, batch_size):
    n_batches = len(ids_list) // batch_size
    print(f"Download split into {n_batches+1} batches.")
    insert_ids = report_query_empty.find("[") + 1
    report_query = []
    for i in range(n_batches + 1):
        report_query.append(
            report_query_empty[:insert_ids]
            + ",".join(ids_list[batch_size * i : batch_size * i + batch_size])
            + report_query_empty[insert_ids:]
        )
    return report_query


# Download data in batches
def _download_report(report_query):
    report_response = []
    for batch in report_query:
        batch_response = requests.get(url=PDBEndpoint.report(), params={"query": batch})
        report_response.append(batch_response.json())
        print(f"Batch {len(report_response)}")
    return report_response


# Merge report batches
def _merge_batches(report_response):
    merged_report = []
    for batch in report_response:
        batch = batch["data"]["entries"]
        merged_report.extend([entry for entry in batch])
    return merged_report


# Convert merged report to data frame. Requires refactor if different report query is used :<
def _json_to_dataframe(merged_report):
    exptl_crystal = pd.json_normalize(merged_report, "exptl_crystal", meta=["rcsb_id"])
    exptl_crystal_grow = pd.json_normalize(merged_report, "exptl_crystal_grow")
    resolution = pd.json_normalize(
        merged_report, ["rcsb_entry_info", "resolution_combined"]
    )
    organism = pd.json_normalize(
        merged_report, ["polymer_entities", "rcsb_entity_source_organism"]
    )
    sequence = pd.json_normalize(merged_report, ["polymer_entities"]).drop(
        "rcsb_entity_source_organism", axis=1
    )

    data_raw = (
        exptl_crystal.join(exptl_crystal_grow)
        .join(resolution)
        .join(organism)
        .join(sequence)
    )
    data_raw.columns = [
        "matthews",
        "percent_solvent",
        "rcsb_id",
        "method",
        "pH",
        "conditions",
        "temp",
        "resolution",
        "organism",
        "sequence",
    ]
    return data_raw

"""Fetches PDB IDs of entries matching a search query.

Args:
    search_json_filename: a str with the path and file name of search query json file

Returns:
    List of PDB IDs of entries matching the search query
"""
def search_PDB(search_json_filename: str):
    with open(search_json_filename, "r") as searchfile_in:
        search_query = searchfile_in.read()

    ids_list = _get_ids_list(search_query)

    return ids_list


"""Fetches PDB report for a list of IDs.

Args:
    ids_list: a list of PDB IDs
    report_json_filename: a str with the path and file name of report query json file
    batch_size: divide the download into batches for large IDs lists. Should be lowered if the PDB server refues connection. 

Returns:
    A pandas DataFrame with the desired PDB report.
"""
def report_from_PDB(ids_list, report_json_filename: str, batch_size=5000):
    with open(report_json_filename, "r") as reportfile_in:
        report_query_empty = reportfile_in.read()

    report_query = _build_report_query(ids_list, report_query_empty, batch_size)

    report_response = _download_report(report_query)

    merged_report = _merge_batches(report_response)

    data_raw = _json_to_dataframe(merged_report)

    return data_raw

"""Saves a pandas DataFrame with raw data to SQL database.

Args: 
    data_raw: dataframe containing raw data. Columns have to match the ones defined in _json_to_dataframe function.

Returns:
    Nothing. Uses pandas DataFrame.to_sql function.

"""
def save_raw_data_to_db(data_raw: pd.DataFrame):
    db_engine = create_db_connection()
    today = date.today()
    today = today.isoformat()
    table_name = f"data_raw_{today}"
    with db_engine.connect() as db_connection:
        data_raw.to_sql(
            name=table_name,
            con=db_engine,
            if_exists="replace",
            index=False,
            chunksize=5000,
            dtype={
                "matthews": Float,
                "percent_solvent": Float,
                "rcsb_id": String,
                "method": Text,
                "pH": Float,
                "conditions": Text,
                "temp": Float,
                "resolution": Float,
                "organism": Text,
                "sequence": Text,
            },
        )

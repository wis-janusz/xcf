#Functionality for downloading PDB report using provided search and report jsons.

import requests
import pandas as pd

#define PDB endpoints
class PDBEndpoint():
    _search = 'https://search.rcsb.org/rcsbsearch/v2/query'
    _report = 'https://data.rcsb.org/graphql'

    @classmethod
    def search (cls):
        return cls._search

    @classmethod
    def report (cls):
        return cls._report

#Search PDB for list of entry IDs
def _get_ids_list(search_query):
        search_response = requests.get(url = PDBEndpoint.search(), params = {'json' : search_query})
        result_set = search_response.json()['result_set']
        ids_list = []
        for item in result_set:
            id = item['identifier']
            add_quotes = f'\"{id}\"'
            ids_list.append(add_quotes)
        return ids_list

#Build a list of report queries to be sent in batches, too large batch size can be denied by the PDB server
def _build_report_query(ids_list, report_query_empty, batch_size):
    n_batches = len(ids_list)//batch_size
    print(f'Download split into {n_batches+1} batches.')
    insert_ids = report_query_empty.find('[')+1
    report_query = []
    for i in range(n_batches+1):
        report_query.append(report_query_empty[:insert_ids] + ','.join(ids_list[batch_size*i:batch_size*i+batch_size]) + report_query_empty[insert_ids:])
    return report_query

#Download data in batches 
def _download_report(report_query):
    report_response = []
    for batch in report_query:
        batch_response = requests.get(url = PDBEndpoint.report(), params = {'query' : batch})
        report_response.append(batch_response.json())
        print(f'Batch {len(report_response)}')
    return report_response
    
#Merge report batches
def _merge_batches(report_response):
    merged_report = []
    for batch in report_response:
        batch = batch['data']['entries']
        merged_report.extend([entry for entry in batch])
    return merged_report

#Convert merged report to data frame. Requires refactor if different report query is used :<
def _json_to_dataframe(merged_report):
    exptl_crystal = pd.json_normalize(merged_report, 'exptl_crystal', meta=['rcsb_id'])
    exptl_crystal_grow = pd.json_normalize(merged_report, 'exptl_crystal_grow')
    resolution = pd.json_normalize(merged_report, ['rcsb_entry_info', 'resolution_combined'])
    organism = pd.json_normalize(merged_report, ['polymer_entities', 'rcsb_entity_source_organism'])
    sequence = pd.json_normalize(merged_report, ['polymer_entities']).drop('rcsb_entity_source_organism', axis=1)

    data_raw = exptl_crystal.join(exptl_crystal_grow).join(resolution).join(organism).join(sequence)
    data_raw.columns = ['matthews','percent_solvent','rcsb_id','method','pH','conditions','temp','resolution','organism','sequence']
    return data_raw

def search_PDB(search_json_filename:str):
    with open(search_json_filename, 'r') as searchfile_in:
        search_query = searchfile_in.read()
        
    ids_list = _get_ids_list(search_query)

    return ids_list

#Remember to lower your batchsize if server denies your connection
def report_from_PDB(ids_list, report_json_filename:str, batch_size = 5000):
    with open(report_json_filename, 'r') as reportfile_in:
        report_query_empty = reportfile_in.read()
        
    report_query = _build_report_query(ids_list, report_query_empty, batch_size)
    
    report_response = _download_report(report_query)
    
    merged_report = _merge_batches(report_response)

    data_raw = _json_to_dataframe(merged_report)

    return data_raw


import requests
import json
import pandas as pd

class PDBEndpoint():
    _search = 'https://search.rcsb.org/rcsbsearch/v1/query'
    _report = 'https://data.rcsb.org/graphql'

    @classmethod
    def search (cls):
        return cls._search

    @classmethod
    def report (cls):
        return cls._report

def get_ids_list(search_query):
        search_response = requests.get(url = PDBEndpoint.search(), params = {'json' : search_query})
        result_set = search_response.json()['result_set']
        ids_list = []
        for item in result_set:
            id = item['identifier']
            add_quotes = f'\"{id}\"'
            ids_list.append(add_quotes)
        return ids_list

def build_report_query(ids_list, report_query_empty, batch_size = 5000):
    n_batches = len(ids_list)//batch_size
    insert_ids = report_query_empty.find('[')+1
    report_query = []
    for i in range(n_batches+1):
        report_query.append(report_query_empty[:insert_ids] + ','.join(ids_list[batch_size*i:batch_size*i+batch_size]) + report_query_empty[insert_ids:])
    return report_query

def download_report(report_query):
    report_response = []
    for batch in report_query:
        report_response.append(requests.get(url = PDBEndpoint.report(), params = {'query' : batch}))
        print(f'Batch {len(report_response)}')
    return report_response

def download_data(search_json_filename:str, report_json_filename:str):
    with open(search_json_filename, 'r') as searchfile_in, open(report_json_filename, 'r') as reportfile_in:
        search_query = searchfile_in.read()
        report_query_empty = reportfile_in.read()

    ids_list = get_ids_list(search_query)
    
    report_query = build_report_query(ids_list, report_query_empty)
    
    report = download_report(report_query)
    
    return report

def merge_batches(report):
    entries = []
    for batch in report:
        batch = batch['data']['entries']
        entries.append([entry for entry in batch])
    return entries

def json_to_csv(entries):
    data_raw = pd.json_normalize(entries)
    data_raw['resolution'] = data_raw['rcsb_entry_info.resolution_combined'].str[0]
    data_raw['matthews'] = data_raw['exptl_crystal'].str[0].str['density_Matthews']
    data_raw['percent_solvent'] = data_raw['exptl_crystal'].str[0].str['density_percent_sol']
    data_raw['method'] = data_raw['exptl_crystal_grow'].str[0].str['method']
    data_raw['pH'] = data_raw['exptl_crystal_grow'].str[0].str['pH']
    data_raw['temp'] = data_raw['exptl_crystal_grow'].str[0].str['temp']
    data_raw['organism'] = data_raw['polymer_entities'].str[0].str['rcsb_entity_source_organism'].str[0].str['ncbi_scientific_name']
    data_raw['sequence'] = data_raw['polymer_entities'].str[0].str['entity_poly'].str['pdbx_seq_one_letter_code_can']
    data_raw['conditions'] = data_raw['exptl_crystal_grow'].str[0].str['pdbx_details']
    data_raw = data_raw.drop(['rcsb_entry_info.resolution_combined','rcsb_entry_container_identifiers.entry_id', 'exptl_crystal', 'exptl_crystal_grow', 'polymer_entities'], axis = 1)
    with open('data_raw.csv', 'w') as file_out:
        data_raw.to_csv(file_out)

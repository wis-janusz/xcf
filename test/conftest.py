import pytest
import pandas as pd

@pytest.fixture
def search_json():
    return 'test/PDBsearch_test.json'

@pytest.fixture
def search_json_len():
    return 144

@pytest.fixture
def report_json():
    return 'test/PDBreport_v1.0.json'

@pytest.fixture
def report_columns():
    return ['matthews','percent_solvent','rcsb_id','method','pH','conditions','temp','resolution','organism','sequence']

@pytest.fixture
def pHpred_data_raw():
    return pd.read_csv('test/data_raw_2022-11-06.csv')[0:1000]

@pytest.fixture
def pHpred_data_clean_columns():
    return ['pH','sequence','len_seq', 'seq_one_hot']

@pytest.fixture
def pHpred_data_clean_len():
    return 873  #873 for firest 1000 raw entries, ph 3-9, length 100-600

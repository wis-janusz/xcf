import pytest

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

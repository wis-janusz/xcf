import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def search_json():
    return 'test/PDBsearch_test.json'

@pytest.fixture
def search_json_len():
    return 145

@pytest.fixture
def report_json():
    return 'test/PDBreport_v1.0.json'

@pytest.fixture
def report_columns():
    return ['matthews','percent_solvent','rcsb_id','method','pH','conditions','temp','resolution','organism','sequence']

@pytest.fixture
def test_df():
    return pd.DataFrame({'column':np.arange(1000)})

@pytest.fixture
def test_split():
    return np.split(pd.DataFrame({'column':np.arange(1000)}).sample(frac=1, random_state=14), [800,900])

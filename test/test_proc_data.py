import xcf

def test_search_PDB(search_json, search_json_len):
    assert len(xcf.search_PDB(search_json)) == search_json_len

def test_pHpred_clener(pHpred_data_raw, pHpred_data_clean_columns, pHpred_data_clean_len):
    data_clean = xcf.process_data(pHpred_data_raw, mode = 'pHpred')
    assert list(data_clean.columns) == pHpred_data_clean_columns
    assert data_clean.shape[0] == pHpred_data_clean_len
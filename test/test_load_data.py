import xcf

def test_search_PDB(search_json, search_json_len):
    assert len(xcf.search_PDB(search_json)) == search_json_len

def test_report_from_PDB(search_json, report_json, report_columns):
    ids_list = xcf.search_PDB(search_json)
    assert list(xcf.report_from_PDB(ids_list, report_json).columns) == report_columns
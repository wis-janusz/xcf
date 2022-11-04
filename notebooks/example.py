import pandas as pd
#columns = ['rcsb_id', 'density_Matthews', 'density_percent_sol', 'method', 'pH','pdbx_details','temp','resolution_combined','pdbx_seq_one_letter_code_can','ncbi_scientific_name']

example = {
        "rcsb_id": "101M",
        "exptl_crystal": [{"density_Matthews": 3.09, "density_percent_sol": 60.2}],
        "exptl_crystal_grow": [
            {
                "method": 'null',
                "pH": 9.0,
                "pdbx_details": "3.0 M AMMONIUM SULFATE, 20 MM TRIS, 1MM EDTA, PH 9.0",
                "temp": 'null',
            }
        ],
        "rcsb_entry_container_identifiers": {"entry_id": "101M"},
        "rcsb_entry_info": {"resolution_combined": [2.07]},
        "polymer_entities": [
            {
                "entity_poly": {
                    "pdbx_seq_one_letter_code_can": "MVLSEGEWQLVLHVWAKVEADVAGHGQDILIRLFKSHPETLEKFDRVKHLKTEAEMKASEDLKKHGVTVLTALGAILKKKGHHEAELKPLAQSHATKHKIPIKYLEFISEAIIHVLHSRHPGNFGADAQGAMNKALELFRKDIAAKYKELGYQG"
                },
                "rcsb_entity_source_organism": [
                    {"ncbi_scientific_name": "Physeter catodon"}
                ],
            }
        ],
    }

exptl_crystal = pd.json_normalize(example, 'exptl_crystal', meta=['rcsb_id'])
exptl_crystal_grow = pd.json_normalize(example, 'exptl_crystal_grow')
resolution = pd.json_normalize(example, ['rcsb_entry_info', 'resolution_combined'])
organism = pd.json_normalize(example, ['polymer_entities', 'rcsb_entity_source_organism'])
sequence = pd.json_normalize(example, ['polymer_entities']).drop('rcsb_entity_source_organism', axis=1)

raw_data = exptl_crystal.join(exptl_crystal_grow).join(resolution).join(organism).join(sequence)
raw_data.columns = ['matthews','percent_solvent','rcsb_id','method','pH','conditions','temp','resolution','organism','sequence']

print(raw_data.T)


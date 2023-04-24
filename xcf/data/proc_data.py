import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy import text
from sqlalchemy.types import Float, Text, Integer
from tensorflow import data
from .db import create_db_connection


class DataProcConfig():
    _modes = ['pHpred']
    _pHpred_range = (3,10)
    _pHpred_seq_range = (100,600)
    _aa_list = ['A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','#']

    @classmethod
    def aa_one_hot_encoder(cls):
        return OneHotEncoder(categories=[cls._aa_list], sparse = False)

    @classmethod
    def list_modes(cls):
        return cls._modes

    @classmethod
    def pHpred_range(cls):
        return cls._pHpred_range

    @classmethod
    def pHpred_seq_range(cls):
        return cls._pHpred_seq_range  


def _pHpred_cleaner(data_raw:pd.DataFrame, pHpred_range:tuple, pHpred_seq_range:tuple) -> pd.DataFrame:
    
    data_proc= data_raw[['rcsb_id', 'pH', 'sequence']].set_index('rcsb_id').dropna()
    data_proc['sequence'] = data_proc['sequence'].astype('string')
    data_proc['len_seq'] = data_proc['sequence'].map(len)
    data_proc = data_proc[(data_proc['pH'] >= pHpred_range[0]) & (data_proc['pH'] <= pHpred_range[1])]
    data_proc = data_proc[(data_proc['len_seq'] >= pHpred_seq_range[0]) & (data_proc['len_seq'] <= pHpred_seq_range[1])]

    return data_proc

def _one_hot_encode_aa(sequence:str, max_len:int, encoder) -> pd.DataFrame:
        
    sequence_padded = sequence.ljust(max_len, '#')
    seq_array = np.array(list(sequence_padded)).reshape(-1,1)
        
    return encoder.fit_transform(seq_array).astype('int8')


"""DEPRECATED: Use load_raw_data_from_db instead.
Takes raw data DataFrame and processes it for pHpred, including one-hot encoding.

Args: 
    data_raw: DataFrame containing raw data.

Returns:
    data_clean: DataFrame with data cleaned for pHpred and one-hot encoding of sequences.

"""
def process_data(data_raw:pd.DataFrame, *, mode:str = 'pHpred') -> pd.DataFrame:

    if mode == 'pHpred':
        data_clean = _pHpred_cleaner(data_raw, DataProcConfig.pHpred_range(), DataProcConfig.pHpred_seq_range())
        data_clean['seq_one_hot']=data_clean['sequence'].apply(lambda s: _one_hot_encode_aa(s, DataProcConfig.pHpred_seq_range()[1], DataProcConfig.aa_one_hot_encoder()))

        return data_clean


def list_raw_data_tables():
    db_engine = create_db_connection()

    with db_engine.connect() as db_connection:
        tables = db_connection.execute(text("SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'data_raw_%'")).all()
        
    return tables

def load_data_from_db(table_name: str, mode:str = 'pHpred') -> pd.DataFrame:
    db_engine = create_db_connection()

    with db_engine.connect() as db_connection:
        data_raw = pd.read_sql_table(table_name, db_connection)
    
    if mode == 'clean':
        data_clean = data_raw.set_index('rcsb_id')
    
    elif mode == 'pHpred':
        data_clean = _pHpred_cleaner(data_raw, DataProcConfig.pHpred_range(), DataProcConfig.pHpred_seq_range())
    
    return data_clean

def save_data_to_db(data_clean: pd.DataFrame, mode:str = 'pHpred', custom_table_name = None, source_table_name = None):
    
    db_engine = create_db_connection()
    with db_engine.connect() as db_connection:
        if mode == 'pHpred':
            if not custom_table_name:
                table_name = f"data_pHpred_from_{source_table_name}"
            else:
                table_name = custom_table_name

            data_clean.to_sql(
                name=table_name,
                con=db_engine,
                if_exists='replace',
                index=True,
                chunksize=5000,
                dtype={
                    "pH": Float,
                    "sequence": Text,
                    "len_seq": Integer
                }
        )

def split_ds(ds: data.Dataset, train=0.8, val=0.1, test=0.1, shuffle=True) -> data.Dataset:
    ds_size = int(data.experimental.cardinality(ds))
    
    assert (train + test + val) == 1
    
    if shuffle:
        ds = ds.shuffle(ds_size, seed=14)
    
    train_size = int(train * ds_size)
    val_size = int(val * ds_size)
    
    train_ds = ds.take(train_size)    
    val_ds = ds.skip(train_size).take(val_size)
    test_ds = ds.skip(train_size).skip(val_size)
    
    return train_ds, val_ds, test_ds

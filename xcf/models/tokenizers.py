
import pandas as pd
AA_VOCAB = ['<PAD>','<START>','<END>','<MASK>','A','B','C','D','E','F','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
MAX_SEQUENCE_LENGTH = 600 #Not counting <START> and <END> tokens

def tokenize_protein(seq:str):
    tokens = [char for char in seq]
    tokens += [AA_VOCAB[0]] * (MAX_SEQUENCE_LENGTH - len(tokens))
    tokens.insert(0,AA_VOCAB[1])
    tokens.append(AA_VOCAB[2])
    ids = []
    for token in tokens:
        ids.append(AA_VOCAB.index(token))
    return pd.Series([tokens, ids])

print(len(AA_VOCAB))

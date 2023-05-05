from keras import Sequential
from keras.metrics import RootMeanSquaredError
from keras.layers import Embedding, Dense, LSTM

def compile_phpred_basic_LSTM(tokenizer, seq_length, embed_dim):
    model = Sequential()
    model.add(Embedding(input_dim=tokenizer.vocabulary_size(), output_dim=embed_dim, input_length=seq_length, mask_zero=True))
    model.add(LSTM(8))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error',optimizer='adam', metrics=[RootMeanSquaredError()])
    return model



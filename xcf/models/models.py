from keras import Sequential, Model
from keras.layers import Input, Masking, Dense, Bidirectional, LSTM, Flatten, Dropout
from keras.metrics import RootMeanSquaredError, Precision, Recall
from keras.optimizers import Adam, SGD, Adagrad

def compile_Liu2017_LSTM(tokenizer, seq_length, n_hidden, dropout, lr, n_classes):
    inputs = Input(shape=(seq_length,tokenizer.vocabulary_size()), dtype = 'float32')

    pad_masking_layer = Masking(mask_value=0.,input_shape=(seq_length,tokenizer.vocabulary_size()))
    pad_maskind_out = pad_masking_layer(inputs)

    lstm_layer = LSTM(n_hidden, dropout=dropout)
    bidirectional_layer = Bidirectional(lstm_layer, merge_mode='concat')
    bidirectional_out = bidirectional_layer(pad_maskind_out)

    out_layer=Dense(n_classes,activation='sigmoid')
    outputs = out_layer(bidirectional_out)

    model = Model(inputs, outputs)
    opt = Adagrad(learning_rate=lr)
    model.compile(loss='binary_crossentropy',optimizer=opt, metrics=[Precision(), Recall()])
    print(model.summary())
    return model

def compile_Liu2017_LSTM_3(tokenizer, seq_length, n_hidden, dropout, lr, n_classes):
    inputs = Input(shape=(seq_length,tokenizer.vocabulary_size()), dtype = 'float32')

    pad_masking_layer = Masking(mask_value=0.,input_shape=(seq_length,tokenizer.vocabulary_size()))
    pad_maskind_out = pad_masking_layer(inputs)

    lstm_layer = LSTM(n_hidden, dropout=dropout)
    bidirectional_layer = Bidirectional(lstm_layer, merge_mode='concat')
    bidirectional_1 = bidirectional_layer(pad_maskind_out)
    bidirecitonal_2 = bidirectional_layer(bidirectional_1)
    bidirectional_out = bidirectional_layer(bidirecitonal_2)

    out_layer=Dense(n_classes,activation='sigmoid')
    outputs = out_layer(bidirectional_out)

    model = Model(inputs, outputs)
    opt = Adagrad(learning_rate=lr)
    model.compile(loss='binary_crossentropy',optimizer=opt, metrics=[Precision(), Recall()])
    print(model.summary())
    return model

def compile_Liu2017_LSTM_reg(tokenizer, seq_length, n_hidden, dropout, lr):
    inputs = Input(shape=(seq_length,tokenizer.vocabulary_size()), dtype = 'float32')

    pad_masking_layer = Masking(mask_value=0.,input_shape=(seq_length,tokenizer.vocabulary_size()))
    pad_maskind_out = pad_masking_layer(inputs)

    lstm_layer = LSTM(n_hidden, dropout=dropout)
    bidirectional_layer = Bidirectional(lstm_layer, merge_mode='concat')
    bidirectional_out = bidirectional_layer(pad_maskind_out)

    out_layer=Dense(1,activation='linear')
    outputs = out_layer(bidirectional_out)

    model = Model(inputs, outputs)
    opt = SGD(learning_rate=lr)
    model.compile(loss='mean_squared_error',optimizer=opt, metrics=[RootMeanSquaredError()])
    print(model.summary())
    return model

def compile_phpred_basic(tokenizer):
    model = Sequential()
    model.add(Flatten())
    model.add(Dense(512))
    model.add(Dropout(rate=0.1))
    model.add(Dense(128))
    model.add(Dropout(rate=0.1))
    model.add(Dense(32))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='mean_squared_error',optimizer='adam', metrics=[RootMeanSquaredError()])
    return model



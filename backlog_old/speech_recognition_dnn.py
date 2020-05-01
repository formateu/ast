from keras import backend as K
from keras.models import Model
from keras.layers import (BatchNormalization, Conv1D, Dense, Input,
                          TimeDistributed, Activation, Bidirectional, SimpleRNN,
                          GRU, LSTM, MaxPooling1D, Dropout)


def conv_rnn(input_dim, filters, kernel_size, conv_stride,
             conv_border_mode, units, output_dim=29):
    """ Build a deep network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))

    # CNN + maxpool
    conv_1d = Conv1D(filters, kernel_size,
                     strides=conv_stride,
                     padding=conv_border_mode,
                     activation='relu',
                     name='conv1d')(input_data)
    # maxpool = MaxPooling1D(pool_size=4, strides=2, padding='valid')(conv_1d)

    # Batch Normalization
    conv1_normalized = BatchNormalization(name="maxpool_normalized")(conv_1d)

    # Bidirectionnal RNN
    bidir_rnn = Bidirectional(
        GRU(units, activation="relu", return_sequences=True,
            implementation=2, name="bidir_rnn"))(conv1_normalized)

    # Batch Normalization
    bidir_rnn_normalized = BatchNormalization(name="bidir_rnn_normalized")(
        bidir_rnn)

    # Time distributed
    time_dense1 = TimeDistributed(Dense(output_dim))(bidir_rnn_normalized)

    # Dropout
    dropout = Dropout(0.4)(time_dense1)

    # Time distributed
    time_dense2 = TimeDistributed(Dense(output_dim))(dropout)

    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense2)

    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)

    # DONE: Specify model.output_length
    model.output_length = lambda x: cnn_output_length(
        x, kernel_size, conv_border_mode, conv_stride)

    print(model.summary())
    return model

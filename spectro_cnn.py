import numpy as np
#from tensorflow.keras.datasets import mnist
from tensorflow.keras.models import Sequential, save_model
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from np_utils import to_categorical
from load_simple_speech import load_data

seed = 7
np.random.seed(seed)

# load data
(X_train, y_train), (X_test, y_test) = load_data()

# y_train = np.array(y_train.tolist())
# y_test = np.array(y_test.tolist())
# reshape to be [samples][pixels][width][height]
X_train = X_train.reshape(X_train.shape[0], 110, 1024, 1).astype('float32')
X_test = X_test.reshape(X_test.shape[0], 110, 1024, 1).astype('float32')
print(X_train.shape)
print(y_train.shape)
print(X_test.shape)
print(y_test.shape)

# one hot encode outputs
y_train = to_categorical(y_train)
y_test = to_categorical(y_test)
num_classes = y_test.shape[1]

# print(num_classes)

def baseline_model():
    # create model
    model = Sequential()
    model.add(Conv2D(32, (50, 50), input_shape=(110, 1024, 1), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(32, (20, 20), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
    # Compile model
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


# build the model
model = baseline_model()
# Fit the model
model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=200, verbose=2)

save_model(model, 'spectro_model')
# Final evaluation of the model
scores = model.evaluate(X_test, y_test, verbose=0)
print("CNN Error: %.2f%%" % (100-scores[1]*100))
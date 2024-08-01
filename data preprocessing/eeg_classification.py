# -*- coding: utf-8 -*-
"""EEG_Classification.ipynb

# Import Libraries
"""

import pandas as pd
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import confusion_matrix


"""# Load data

"""

# Load the data for Machine Learning task
data = pd.read_csv('merged_data.csv')
print(data.head())

# Split the data into features and target
X = data.iloc[:, :-1].values  # Features
y = data.iloc[:, -1].values  # Target
feature_names = data.columns[:-1].to_list()  # Feature names

# Print the shape of features and target
print(f'Features shape: {X.shape}')
print(f'Target shape: {y.shape}')
print(f'Feature names: {feature_names}')

"""# Preprocessing"""

# Replace feature value which its absolute value is less than 10
X = np.where(np.abs(X) < 10, np.nan, X)  # Replace values less than 10 with NaN
X = np.where(np.isnan(X), np.nanmean(X, axis=0), X) # Replace NaN values with mean of the column
# Normalize the data
scaler = MinMaxScaler()
X = scaler.fit_transform(X)
print(X[:10])

# Reshape data
num_intervals = 12
timestamps = 100
features = 6
X = X.reshape(num_intervals, timestamps, features)
print(X.shape)
y = y.reshape(num_intervals, timestamps)
y = y.mean(axis=1)
print(y.shape)

# One-hot Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)
y = to_categorical(y)
print(y)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=4, random_state=42)

"""# Build and Train LSTM model"""

# Build the LSTM model
model = Sequential()
model.add(LSTM(100, input_shape=(timestamps, features), return_sequences=False))
model.add(Dense(25, activation='relu'))
model.add(Dense(y.shape[1], activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X, y, epochs=30, batch_size=4)

# Train the model
model.fit(X_train, y_train, epochs=30, batch_size=4, validation_split=0.2)

"""# Evaluate Model and Save Model"""

# Evaluate the model
loss, accuracy = model.evaluate(X_test, y_test)
print(f'Accuracy: {accuracy:.2f}')

# Make predictions
predictions = model.predict(X_test)

# Convert softmax output to class indices
predicted_classes = np.argmax(predictions, axis=-1)

# Convert class indices to one-hot encoded vectors
predicted_one_hot = np.array([to_categorical(pred, num_classes=4) for pred in predicted_classes])
print(predicted_one_hot)
print(y_test)

# Save the model
model.save('lstm_model.h5')
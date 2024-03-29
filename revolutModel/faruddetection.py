# -*- coding: utf-8 -*-
"""FarudDetection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KcnQ9GP2stmNPnxVESKKE2unX_Hp6yrs

***Import Libraries***
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

"""***Mount Google Drive***"""

from google.colab import drive
#Import drive as get file from the drive
drive.mount('/content/drive')

"""**Data Preperation**"""

# Specify the path of CSV file
file_path = '/content/drive/MyDrive/Deep Learning/DL-CW/Revolut-Customer-Fraud-Data/'

#use pandas library to read the csv file
transaction_df = pd.read_csv(file_path+'transactions.csv') #transaction file
users_df = pd.read_csv(file_path+'users.csv') #users files
farud_user_df = pd.read_csv(file_path+'fraudsters.csv') #farud file

# Display the DataFrame
print(transaction_df.head())
print(users_df.head())
print(farud_user_df.head())

transaction_df = transaction_df.drop(['ID'], axis = 1)

transaction_df['TRNS_DATE'] = pd.to_datetime(transaction_df['CREATED_DATE'])
transaction_df = transaction_df.drop(['CREATED_DATE'], axis = 1)
print(transaction_df.head())

# Extract date-related features
transaction_df['TDate'] = transaction_df['TRNS_DATE'].dt.date
transaction_df['Day'] = transaction_df['TRNS_DATE'].dt.day_name()
transaction_df['Month'] = transaction_df['TRNS_DATE'].dt.month_name()
transaction_df['Year'] = transaction_df['TRNS_DATE'].dt.year

#Data Preprocessing make boolean for fraud or not fraud user by given list
transaction_df['IS_FRAUD'] = transaction_df['USER_ID'].isin(farud_user_df['USER_ID']).astype(int)

# Create a mapping dictionary from 'USER_ID' to 'Age' in the Users sheet
user_age = dict(zip(users_df['ID'], (pd.to_datetime('now') - pd.to_datetime(users_df['BIRTH_DATE'])).astype('<m8[Y]')))

# Apply the mapping to create a new 'Age' column in the Transactions sheet
transaction_df['Age'] = round(transaction_df['USER_ID'].map(user_age)).astype(int)

transaction_df.head()

# Calculate the frequency of transactions for each user in the target month and year
transaction_df['TRNS_FREQUENCY_PER_M'] = transaction_df.groupby(['USER_ID', 'Month', 'Year'])['TRNS_DATE'].transform('count')
transaction_df['TRNS_FREQUENCY_PER_DATE'] = transaction_df.groupby(['USER_ID', 'TDate'])['TRNS_DATE'].transform('count')

# Calculate the total amount transaction by each user in the target month and year
transaction_df['TRANS_AMOUNT_PER_M'] = transaction_df.groupby(['USER_ID', 'Month', 'Year'])['AMOUNT_GBP'].transform('sum')

# Filter transactions with STATE = 'COMPLETED'
completed_transactions = transaction_df[transaction_df['STATE'] == 'COMPLETED']

# Group by 'USER_ID' and 'TDate' and sum the 'AMOUNT_GBP' for each user and date
transaction_df['TRANS_AMOUNT_PER_DATE'] = completed_transactions.groupby(['USER_ID', 'TDate'])['AMOUNT_GBP'].transform('sum')

transaction_df['T_DATE'] = transaction_df['TRNS_DATE'].dt.date
# Create a new column 'Douplicate_Transaction' based on duplicate amounts within the same date
transaction_df['Douplicate_Transaction'] = transaction_df.duplicated(subset=['USER_ID', 'AMOUNT_GBP', 'T_DATE'], keep=False).astype(int)

# Create a new column 'total_unique_transactions_per_user_date' based on unique transaction within the same date
transaction_df['Uni_Tran_PER_Day'] = transaction_df.groupby(['USER_ID', 'T_DATE'])['AMOUNT_GBP'].transform('nunique')
transaction_df['Trans_PER_Day'] = transaction_df.groupby(['USER_ID', 'T_DATE'])['AMOUNT_GBP'].transform('count')

pd.set_option('display.float_format', lambda x: '%.1f' % x)
stats_df = transaction_df.describe()
print(stats_df)

# Create a DataFrame for visualization
stats_df = pd.DataFrame({
    'Statistic': ['mean', 'std', 'min', '25%', '50%', '75%', 'max'],
    'Value': [stats_df['Trans_PER_Day']['mean'], stats_df['Trans_PER_Day']['std'], stats_df['Trans_PER_Day']['min'],
              stats_df['Trans_PER_Day']['25%'], stats_df['Trans_PER_Day']['50%'], stats_df['Trans_PER_Day']['75%'], stats_df['Trans_PER_Day']['max']]
})

# Bar plot with a custom color scale
fig = px.bar(stats_df, x='Statistic', y='Value',
             title='Summary Statistics of Debit Per Day',
             labels={'Statistic': 'Statistic', 'Value': 'Value'},
             color='Value',
             color_continuous_scale='Viridis',  # Choose a color scale of your preference
             height=400)

# Customize layout
fig.update_layout(xaxis_title='Statistic for the Debit Per Day', yaxis_title='Value', coloraxis_showscale=False)
fig.show()

# Calculate the count of each transaction status
status_counts = transaction_df['STATE'].value_counts().reset_index()

# Rename columns for clarity
status_counts.columns = ['STATE', 'Count']

# Create an interactive pie chart using plotly
fig = px.pie(status_counts, values='Count', names='STATE', title='Transaction Status Distribution',
             labels={'STATE': 'Transaction Status', 'Count': 'Count'},
             color_discrete_sequence=px.colors.sequential.RdBu,
             hole=0.3,
             template='plotly_dark')

# Display the chart
fig.show()

import plotly.express as px
import pandas as pd

# Calculate the count of each transaction type
type_counts = transaction_df['TYPE'].value_counts().reset_index()

# Rename columns for clarity
type_counts.columns = ['TYPE', 'Count']

# Create an interactive donut chart using plotly
fig = px.pie(type_counts, values='Count', names='TYPE', hole=0.3, title='Transaction Types Distribution',
             labels={'TYPE': 'Transaction Type', 'Count': 'Count'},
             template='plotly_dark')

# Display the chart
fig.show()

# Convert State to Code
status_mapping = {'FAILED': 0, 'COMPLETED': 1, 'REVERTED': 2, 'DECLINED': 3}

# Create a new column 'Status_Code' based on the mapping
transaction_df['State_Code'] = transaction_df['STATE'].map(status_mapping)

# Convert Type to Code
type_mapping = {'TOPUP': 0, 'CARD_PAYMENT': 1, 'FEE': 2, 'EXCHANGE': 3, 'TRANSFER': 4, 'ATM': 5}

# Create a new column 'TRANS_TYPE_Code' based on the mapping
transaction_df['Trans_Type_Code'] = transaction_df['TYPE'].map(type_mapping)

df_no_duplicates = transaction_df.drop_duplicates()

# Assuming 'USER_ID', 'MONTH', and 'YEAR' are given values
given_user_id = 'fd7f3ff6-0ed6-4a85-a7b5-2f205e0ef72f'  # Replace with the actual USER_ID
given_month = 'April'      # Replace with the actual MONTH
given_year = 2019    # Replace with the actual YEAR


# Filter the DataFrame based on the given USER_ID, MONTH, and YEAR
filtered_data = transaction_df[(transaction_df['USER_ID'] == given_user_id) &
                                (transaction_df['Month'] == given_month) &
                                (transaction_df['Year'] == given_year)]

# Display the filtered data
print(filtered_data)

# Drop duplicate transactions based on USER_ID, AMOUNT_GBP, and T_DATE
transaction_df = transaction_df.drop_duplicates(subset=['USER_ID', 'AMOUNT_GBP', 'T_DATE'], keep='first')

df_no_duplicates = transaction_df.drop_duplicates()


# Assuming 'USER_ID', 'MONTH', and 'YEAR' are given values
given_user_id = 'fd7f3ff6-0ed6-4a85-a7b5-2f205e0ef72f'  # Replace with the actual USER_ID
given_month = 'April'      # Replace with the actual MONTH
given_year = 2019    # Replace with the actual YEAR


# Filter the DataFrame based on the given USER_ID, MONTH, and YEAR
filtered_data = transaction_df[(transaction_df['USER_ID'] == given_user_id) &
                                (transaction_df['Month'] == given_month) &
                                (transaction_df['Year'] == given_year)]

# Display the filtered data
print(filtered_data)

# Drop STATE, columns
columns_to_drop = ['STATE', 'Douplicate_Transaction']
transaction_df.drop(columns=columns_to_drop, inplace=True)

transaction_df.head()

# Create a histogram of transactions per currency
fig = px.histogram(transaction_df, x='CURRENCY', title='Transaction Count by Currency')

# Show the plot
fig.show()

# Sort DataFrame by timestamp
transaction_df = transaction_df.sort_values(by='TRNS_DATE')

# Calculate the last 5 average transaction amount
transaction_df['Last_5_Avg_Amount'] = transaction_df['AMOUNT_GBP'].rolling(window=5, min_periods=1).mean()

# Display the result
print(transaction_df)

"""Checking Imbalanced data"""

# Check the Fraud Class distribution to check imbalance data

class_counts = transaction_df['IS_FRAUD'].value_counts()
print(class_counts)

transaction_df['IS_FRAUD'].value_counts().plot(kind='bar')
plt.title('Class Distribution')
plt.xlabel('Class')
plt.ylabel('Count')
plt.show()

class_percentages = transaction_df['IS_FRAUD'].value_counts(normalize=True)
print(class_percentages)


imbalance_ratio = class_counts[1] / class_counts[0]
print(f"Imbalance Ratio: {imbalance_ratio}")

#fill all NAN to 0
transaction_df = transaction_df.fillna(0)

transaction_df.head()
# Select columns with numerical data
numerical_columns = transaction_df.select_dtypes(include=['number']).columns

# Print the numerical columns
print("Numerical Columns:")
print(numerical_columns)
numerical_columns_array = np.array(numerical_columns)

# Print the numerical columns as an array
print("Numerical Columns:")
print(numerical_columns_array)

"""LASTM class and Using smote"""

from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.metrics import confusion_matrix, classification_report

class FraudDetectionLSTM:
    def __init__(self, data, features, target, epochs=10, batch_size=10):
        # Initialize the FraudDetectionLSTM class
        self.data = data
        self.features = features
        self.target = target
        self.scaler = MinMaxScaler()
        self.model = None
        self.history = None
        self.epochs = epochs
        self.batch_size = batch_size

    def preprocess_data(self):
        # Normalize the features using Min-Max scaling
        self.data[self.features] = self.scaler.fit_transform(self.data[self.features])

    def apply_smote(self):
        # Apply Synthetic Minority Over-sampling Technique (SMOTE) to handle class imbalance
        # Separate features and target variable
        X = self.data[self.features]
        y = self.data[self.target]

        # Apply SMOTE to the entire dataset
        smote = SMOTE(random_state=42)
        X_resampled, y_resampled = smote.fit_resample(X, y)

        # Update the dataset with the resampled data
        self.data = pd.DataFrame(X_resampled, columns=self.features)
        self.data[self.target] = y_resampled

    def train_test_split(self):
        # Split the dataset into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            self.data[self.features], self.data[self.target],
            test_size=0.2, random_state=42, stratify=self.data[self.target]
        )

        # Reshape for LSTM input
        X_train = X_train.values.reshape((X_train.shape[0], 1, X_train.shape[1]))
        X_test = X_test.values.reshape((X_test.shape[0], 1, X_test.shape[1]))

        return X_train, X_test, y_train, y_test

    def build_model(self):
        # Build the LSTM model
        model = Sequential()
        model.add(LSTM(50, input_shape=(1, self.data[self.features].shape[1]), return_sequences=True))
        model.add(LSTM(50, return_sequences=True))
        model.add(LSTM(50))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1, activation='sigmoid'))

        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        self.model = model

    def train_model(self, X_train, y_train, validation_data=None):
        # Train the LSTM model
        self.history = self.model.fit(
            X_train, y_train,
            epochs=self.epochs,
            batch_size=self.batch_size,
            validation_data=validation_data,
            verbose=2
        )

    def plot_learning_curves(self):
        # Plot the learning curves (accuracy over epochs)
        plt.plot(self.history.history['accuracy'], label='Training Accuracy')
        plt.plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        plt.title('Training and Validation Accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.show()

    def make_predictions(self, X_test):
        # Make predictions using the trained model
        return self.model.predict(X_test)

    def plot_prediction_curve(self, y_true, y_pred):
        # Plot the fraud prediction curve
        plt.plot(y_true.values, label='True Fraud')
        plt.plot(y_pred, label='Predicted Fraud (Probability)')
        plt.title('Fraud Prediction Curve')
        plt.xlabel('Sample Index')
        plt.ylabel('Fraud Probability')
        plt.legend()
        plt.show()

    def evaluate_model(self, X_test, y_test):
        # Evaluate the model using confusion matrix and classification report
        y_pred = self.make_predictions(X_test)
        y_pred_binary = (y_pred > 0.5).astype(int)
        cm = confusion_matrix(y_test, y_pred_binary)

        print("Confusion Matrix:")
        print(cm)

        # Plot the confusion matrix
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='g', cmap='Blues', cbar=False,
                    xticklabels=['Non-Fraud', 'Fraud'],
                    yticklabels=['Non-Fraud', 'Fraud'])
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.show()

        # Classification Report
        report = classification_report(y_test, y_pred_binary)
        print("Classification Report:")
        print(report)
        report = classification_report(y_test, y_pred_binary)
        print("Classification Report:")
        print(report)

    def run(self):
        # Execute the entire process
        self.preprocess_data()
        self.apply_smote()
        X_train, X_test, y_train, y_test = self.train_test_split()
        self.build_model()
        self.train_model(X_train, y_train, validation_data=(X_test, y_test))
        self.plot_learning_curves()
        self.evaluate_model(X_test, y_test)
        y_pred = self.make_predictions(X_test)
        self.plot_prediction_curve
        self.eveluate_model(self, X_test, y_test)

selected_features = numerical_columns_array

fraud_detection = FraudDetectionLSTM(transaction_df, selected_features, 'IS_FRAUD', epochs=10, batch_size=12)
fraud_detection.run()

"""**Model Auto Encoder**


---


"""

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
import matplotlib.pyplot as plt
import pandas as pd

# Assuming 'data' contains your features data and 'IS_FRAUD' contains the corresponding labels

# Select features and labels
features = ['AMOUNT_GBP', 'Year', 'Age', 'TRNS_FREQUENCY_PER_M',
            'TRNS_FREQUENCY_PER_DATE', 'TRANS_AMOUNT_PER_M', 'TRANS_AMOUNT_PER_DATE',
            'Uni_Tran_PER_Day', 'Trans_PER_Day', 'State_Code', 'Trans_Type_Code',
            'Last_5_Avg_Amount']

labels = 'IS_FRAUD'

# Apply SMOTE to handle class imbalance
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(transaction_df[features], transaction_df[labels])

# Preprocess the resampled data
scaler = StandardScaler()
data_scaled = scaler.fit_transform(X_resampled)

# Split the data into training and testing sets
X_train, X_test, _, _ = train_test_split(data_scaled, y_resampled, test_size=0.2, random_state=42, stratify=y_resampled)

# Define the autoencoder architecture
input_dim = X_train.shape[1]

input_layer = Input(shape=(input_dim,))
encoded = Dense(32, activation='relu')(input_layer)
decoded = Dense(input_dim, activation='sigmoid')(encoded)

autoencoder = Model(input_layer, decoded)

# Compile the model
autoencoder.compile(optimizer='adam', loss='mse')

# Train the autoencoder
autoencoder.fit(X_train, X_train, epochs=50, batch_size=32, shuffle=True, validation_data=(X_test, X_test))

# Make predictions on the test set
reconstructed_data = autoencoder.predict(X_test)

# Calculate the reconstruction error
mse = tf.keras.losses.MeanSquaredError()
reconstruction_error = mse(X_test, reconstructed_data).numpy()

# Plot original and reconstructed samples
n = 5  # Number of samples to visualize
plt.figure(figsize=(20, 4))
for i in range(n):
    # Original
    ax = plt.subplot(2, n, i + 1)
    plt.plot(X_test[i])  # Adjust the plot based on your data structure
    plt.title(f"Sample {i + 1} (Original)")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    # Reconstructed
    ax = plt.subplot(2, n, i + 1 + n)
    plt.plot(reconstructed_data[i])  # Adjust the plot based on your data structure
    plt.title(f"Sample {i + 1} (Reconstructed)")
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
plt.show()

# Print reconstruction error
print("Reconstruction Error:", reconstruction_error)
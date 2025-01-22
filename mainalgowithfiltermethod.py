# -*- coding: utf-8 -*-
"""MainAlgoWithFilterMethod.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1LcvCIcu6Q2eZU2Pei4SBRck6kXOmIJhA
"""

# Step 1: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Step 2: Load the Dataset
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Replace 'path_to_your_file.csv' with the actual path to your file in Google Drive
file_path = '/content/drive/My Drive/Datasets/ASEAN_cleaned.csv'

# Load the dataset into a Pandas DataFrame
data = pd.read_csv(file_path)

# Step 3: Display Dataset Info
print("Dataset Loaded Successfully!")
print("First 5 rows of the dataset:")
print(data.head())
print("\nDataset Info:")
print(data.info())

# Prepare the Dataset
data = data.dropna()  # Drop rows with missing values
X = data.select_dtypes(include=[np.number]).drop(columns=["Food supply (kcal)"])
y = data["Food supply (kcal)"]

# Feature Selection using Filter Method (Correlation Analysis)
filter_selector = SelectKBest(score_func=f_regression, k=4)
X_filter_selected = filter_selector.fit_transform(X, y)
selected_features = X.columns[filter_selector.get_support()]
print("Selected Features using Correlation Analysis:", selected_features)

# Reduce the dataset to selected features
X_filtered = X[selected_features]
print("\nReduced Dataset with Selected Features:")
print(X_filtered.head())

# Split data
X_train, X_temp, y_train, y_temp = train_test_split(X_filtered, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=1/3, random_state=42)

# Function to calculate and return evaluation metrics
def evaluate_model(model, X_val, X_test, y_val, y_test, model_name):
    y_val_pred = model.predict(X_val)
    y_test_pred = model.predict(X_test)
    val_metrics = {
        "MAE": mean_absolute_error(y_val, y_val_pred),
        "MSE": mean_squared_error(y_val, y_val_pred),
        "R²": r2_score(y_val, y_val_pred),
    }
    test_metrics = {
        "MAE": mean_absolute_error(y_test, y_test_pred),
        "MSE": mean_squared_error(y_test, y_test_pred),
        "R²": r2_score(y_test, y_test_pred),
    }
    print(f"\n{model_name} - Holdout Validation Metrics:")
    print("Validation:", val_metrics)
    print("Test:", test_metrics)
    return val_metrics, test_metrics

# Function to evaluate K-Fold Cross-Validation metrics
def evaluate_kfold(model, X, y, kf, model_name):
    cv_scores = cross_val_score(model, X, y, scoring='neg_mean_squared_error', cv=kf)
    print(f"\n{model_name} - K-Fold Cross-Validation Metrics:")
    print("Mean MSE:", -np.mean(cv_scores))
    print("Standard Deviation of MSE:", np.std(cv_scores))
    return -np.mean(cv_scores), np.std(cv_scores)

# K-Fold setup
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# Random Forest
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
rf_val_metrics, rf_test_metrics = evaluate_model(rf_model, X_val, X_test, y_val, y_test, "Random Forest")
rf_kfold_mean, rf_kfold_std = evaluate_kfold(rf_model, X_filtered, y, kf, "Random Forest")

# Linear Regression
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
lr_val_metrics, lr_test_metrics = evaluate_model(lr_model, X_val, X_test, y_val, y_test, "Linear Regression")
lr_kfold_mean, lr_kfold_std = evaluate_kfold(lr_model, X_filtered, y, kf, "Linear Regression")

# K-Nearest Neighbors
knn_model = KNeighborsRegressor(n_neighbors=5)
knn_model.fit(X_train, y_train)
knn_val_metrics, knn_test_metrics = evaluate_model(knn_model, X_val, X_test, y_val, y_test, "K-Nearest Neighbors")
knn_kfold_mean, knn_kfold_std = evaluate_kfold(knn_model, X_filtered, y, kf, "K-Nearest Neighbors")

# Support Vector Machine
svm_model = SVR(kernel='rbf', C=1.0, gamma=0.1)
svm_model.fit(X_train, y_train)
svm_val_metrics, svm_test_metrics = evaluate_model(svm_model, X_val, X_test, y_val, y_test, "Support Vector Machine")
svm_kfold_mean, svm_kfold_std = evaluate_kfold(svm_model, X_filtered, y, kf, "Support Vector Machine")

# Summarize Metrics
summary = {
    "Model": ["Random Forest", "Linear Regression", "K-Nearest Neighbors", "Support Vector Machine"],
    "Validation MAE": [rf_val_metrics["MAE"], lr_val_metrics["MAE"], knn_val_metrics["MAE"], svm_val_metrics["MAE"]],
    "Test MAE": [rf_test_metrics["MAE"], lr_test_metrics["MAE"], knn_test_metrics["MAE"], svm_test_metrics["MAE"]],
    "K-Fold Mean MSE": [rf_kfold_mean, lr_kfold_mean, knn_kfold_mean, svm_kfold_mean],
    "K-Fold Std MSE": [rf_kfold_std, lr_kfold_std, knn_kfold_std, svm_kfold_std],
}

# Display Summary
summary_df = pd.DataFrame(summary)
print("\nModel Evaluation Summary:")
print(summary_df)

# prompt: Do separate visualisation for comparison of Validation MAE, Test MAE, K-Fold Mean MSE and K-Fold Std MSE for each algorithm

import matplotlib.pyplot as plt

# Create subplots for each metric
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Plot Validation MAE
axes[0, 0].bar(summary_df["Model"], summary_df["Validation MAE"])
axes[0, 0].set_title("Validation MAE")
axes[0, 0].set_xlabel("Model")
axes[0, 0].set_ylabel("MAE")
axes[0,0].tick_params(axis='x', rotation=45)

# Plot Test MAE
axes[0, 1].bar(summary_df["Model"], summary_df["Test MAE"])
axes[0, 1].set_title("Test MAE")
axes[0, 1].set_xlabel("Model")
axes[0, 1].set_ylabel("MAE")
axes[0, 1].tick_params(axis='x', rotation=45)

# Plot K-Fold Mean MSE
axes[1, 0].bar(summary_df["Model"], summary_df["K-Fold Mean MSE"])
axes[1, 0].set_title("K-Fold Mean MSE")
axes[1, 0].set_xlabel("Model")
axes[1, 0].set_ylabel("MSE")
axes[1, 0].tick_params(axis='x', rotation=45)

# Plot K-Fold Std MSE
axes[1, 1].bar(summary_df["Model"], summary_df["K-Fold Std MSE"])
axes[1, 1].set_title("K-Fold Std MSE")
axes[1, 1].set_xlabel("Model")
axes[1, 1].set_ylabel("MSE")
axes[1, 1].tick_params(axis='x', rotation=45)

# Adjust layout and display the plot
plt.tight_layout()
plt.show()

# prompt: Do visualisation for comparison for each algorithm

import matplotlib.pyplot as plt
import seaborn as sns

# Assuming 'summary_df' is the DataFrame from the previous code
# ... (Your existing code) ...

# Visualization 1: Bar Plot for MAE Comparison
plt.figure(figsize=(10, 6))
sns.barplot(x="Model", y="Validation MAE", data=summary_df)
plt.title("Validation MAE Comparison")
plt.xlabel("Model")
plt.ylabel("MAE")
plt.show()

plt.figure(figsize=(10, 6))
sns.barplot(x="Model", y="Test MAE", data=summary_df)
plt.title("Test MAE Comparison")
plt.xlabel("Model")
plt.ylabel("MAE")
plt.show()


# Visualization 2: Bar Plot for K-Fold MSE Comparison
plt.figure(figsize=(10, 6))
sns.barplot(x="Model", y="K-Fold Mean MSE", data=summary_df)
plt.title("K-Fold Mean MSE Comparison")
plt.xlabel("Model")
plt.ylabel("Mean MSE")
plt.show()

# Visualization 3: Combine MAE and K-Fold MSE
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.barplot(x="Model", y="Test MAE", data=summary_df)
plt.title("Test MAE")

plt.subplot(1, 2, 2)
sns.barplot(x="Model", y="K-Fold Mean MSE", data=summary_df)
plt.title("K-Fold Mean MSE")
plt.tight_layout()
plt.show()

# prompt: Do visualisation to compare the four algorithm

# Visualization 1: Bar Plot for MAE Comparison
plt.figure(figsize=(10, 6))
sns.barplot(x="Model", y="Validation MAE", data=summary_df)
plt.title("Validation MAE Comparison")
plt.xlabel("Model")
plt.ylabel("MAE")
plt.show()

plt.figure(figsize=(10, 6))
sns.barplot(x="Model", y="Test MAE", data=summary_df)
plt.title("Test MAE Comparison")
plt.xlabel("Model")
plt.ylabel("MAE")
plt.show()


# Visualization 2: Bar Plot for K-Fold MSE Comparison
plt.figure(figsize=(10, 6))
sns.barplot(x="Model", y="K-Fold Mean MSE", data=summary_df)
plt.title("K-Fold Mean MSE Comparison")
plt.xlabel("Model")
plt.ylabel("Mean MSE")
plt.show()

# Visualization 3: Combine MAE and K-Fold MSE
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
sns.barplot(x="Model", y="Test MAE", data=summary_df)
plt.title("Test MAE")

plt.subplot(1, 2, 2)
sns.barplot(x="Model", y="K-Fold Mean MSE", data=summary_df)
plt.title("K-Fold Mean MSE")
plt.tight_layout()
plt.show()

# prompt: Model evaluation summary including holdout validation

# Assuming the code you provided is already executed and the variables are defined

# Create a summary DataFrame (This part is already in the provided code)
summary = {
    "Model": ["Random Forest", "Linear Regression", "K-Nearest Neighbors", "Support Vector Machine"],
    "Validation MAE": [rf_val_metrics["MAE"], lr_val_metrics["MAE"], knn_val_metrics["MAE"], svm_val_metrics["MAE"]],
    "Test MAE": [rf_test_metrics["MAE"], lr_test_metrics["MAE"], knn_test_metrics["MAE"], svm_test_metrics["MAE"]],
    "Validation MSE": [rf_val_metrics["MSE"], lr_val_metrics["MSE"], knn_val_metrics["MSE"], svm_val_metrics["MSE"]],
    "Test MSE": [rf_test_metrics["MSE"], lr_test_metrics["MSE"], knn_test_metrics["MSE"], svm_test_metrics["MSE"]],
    "Validation R²": [rf_val_metrics["R²"], lr_val_metrics["R²"], knn_val_metrics["R²"], svm_val_metrics["R²"]],
    "Test R²": [rf_test_metrics["R²"], lr_test_metrics["R²"], knn_test_metrics["R²"], svm_test_metrics["R²"]],
    "K-Fold Mean MSE": [rf_kfold_mean, lr_kfold_mean, knn_kfold_mean, svm_kfold_mean],
    "K-Fold Std MSE": [rf_kfold_std, lr_kfold_std, knn_kfold_std, svm_kfold_std],
}

summary_df = pd.DataFrame(summary)
print("\nModel Evaluation Summary:")
summary_df

# @title Model

from matplotlib import pyplot as plt
import seaborn as sns
summary_df.groupby('Model').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
plt.gca().spines[['top', 'right',]].set_visible(False)
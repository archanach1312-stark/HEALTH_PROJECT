import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_csv("dataset.csv")

# Create target (risk)
disease_cols = [
    'Heart Disease', 'Diabetes', 'Stroke', 'Kidney Disease',
    'Cancer', "Alzheimer's Disease", 'COPD',
    'Liver Disease', "Parkinson's Disease", 'Tuberculosis'
]

data['risk'] = data[disease_cols].max(axis=1)

# Features
X = data[['Age', 'Gender', 'Blood Pressure', 'Cholesterol',
          'Glucose', 'Smoking', 'Alcohol Consumption',
          'Exercise', 'BMI', 'Family History']]

# Convert categorical
X = pd.get_dummies(X)

# Target
y = data['risk']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)

# Save everything
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(X.columns, open("columns.pkl", "wb"))
pickle.dump(accuracy, open("accuracy.pkl", "wb"))

print("✅ Model trained successfully!")
print("🎯 Accuracy:", round(accuracy*100, 2), "%")

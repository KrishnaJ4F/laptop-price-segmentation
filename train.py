import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from urllib.parse import quote_plus as quote
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Configuration
FEATURES = ['Brand', 'Series', 'CPU', 'GPU', 'OS', 'RAM_GB', 'Storage_GB', 'Display_inches', 'Weight_KG', 'Rating']
TARGET = 'Price_Category'

def clean_ram(val):
    if isinstance(val, (int, float)): return val
    val_str = str(val).lower()
    if 'tb' in val_str:
        return float(val_str.replace('tb', '').strip()) * 1024
    return float(val_str.replace('gb', '').strip())

def train_model():
    # Load data
    if os.path.exists('data/laptop_cleaned.csv'):
        print("Loading from cleaned CSV.")
        df = pd.read_csv('data/laptop_cleaned.csv')
    else:
        try:
            pw = "YourPasswordHere" 
            encoded_pw = quote(pw)
            engine = create_engine(f"mysql+pymysql://root:{encoded_pw}@localhost/flipkart_laptops_db")
            df = pd.read_sql("SELECT * FROM laptops_clustered", engine)
            print("Data loaded from MySQL.")
        except:
            print("MySQL fail, loading from laptop.csv.")
            df = pd.read_csv('data/laptop.csv')

    # Feature Engineering
    df = df.replace('Not Available', np.nan)
    
    # Ensure Target existence
    if TARGET not in df.columns:
        if 'Price(Rs)' in df.columns:
            df['Price(Rs)'] = pd.to_numeric(df['Price(Rs)'], errors='coerce')
            bins = [0, 40000, 60000, 90000, float('inf')]
            labels = ['Low', 'Medium', 'High', 'Premium']
            df[TARGET] = pd.cut(df['Price(Rs)'], bins=bins, labels=labels)
        else:
            raise ValueError("Target column and Price(Rs) missing from dataset.")

    # Fill missing numeric values and ensure types
    for col in ['RAM_GB', 'Storage_GB', 'Display_inches', 'Weight_KG', 'Rating']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].median())
        else:
            # Fallback if specific cleaned columns are missing but raw ones exist
            if col == 'RAM_GB' and 'RAM' in df.columns:
                df['RAM_GB'] = df['RAM'].apply(clean_ram)
            else:
                df[col] = 0.0 # Extreme fallback

    # Filtering for selected features
    df = df[FEATURES + [TARGET]]

    # Encoding
    encoders = {}
    df_encoded = df.copy()
    for col in ['Brand', 'Series', 'CPU', 'GPU', 'OS']:
        le = LabelEncoder()
        df_encoded[col] = le.fit_transform(df[col].astype(str))
        encoders[col] = le
    
    target_le = LabelEncoder()
    df_encoded[TARGET] = target_le.fit_transform(df[TARGET].astype(str))
    encoders[TARGET] = target_le

    # Split
    X = df_encoded[FEATURES]
    y = df_encoded[TARGET]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

    # Train
    print("Training Random Forest...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Save Artifacts
    joblib.dump(model, 'laptop_model.pkl')
    joblib.dump(scaler, 'laptop_scaler.pkl')
    joblib.dump(encoders, 'laptop_encoders.pkl')
    print("Model and preprocessors saved successfully.")

if __name__ == "__main__":
    train_model()

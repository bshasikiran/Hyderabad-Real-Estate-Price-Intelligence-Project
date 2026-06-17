"""
Step 4: Random Forest Price Prediction Model
Trains on cleaned data and provides predict_price() function
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import warnings
warnings.filterwarnings('ignore')

# Load cleaned data
df = pd.read_csv('hyderabad_properties_cleaned.csv')

print("Training ML Model...")

# Prepare features
le = LabelEncoder()
df['locality_encoded'] = le.fit_transform(df['locality'])

features = ['locality_encoded', 'bhk', 'sqft', 'has_gym', 'has_pool', 'has_parking']
X = df[features]
y = df['price']

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest Model
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    min_samples_split=5,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Model Performance:")
print(f"Mean Absolute Error: ₹{mae:,.0f}")
print(f"R² Score: {r2:.3f}")

# Save model and encoder
joblib.dump(model, 'price_prediction_model.pkl')
joblib.dump(le, 'locality_encoder.pkl')
print("\nModel saved as price_prediction_model.pkl")
print("Encoder saved as locality_encoder.pkl")

# === predict_price() Function ===
def predict_price(locality, bhk, sqft, has_gym=0, has_pool=0, has_parking=1):
    """
    Predict fair price for a property in Hyderabad.
    
    Parameters:
    - locality: str (e.g., 'Kondapur', 'Madhapur')
    - bhk: int (1-4)
    - sqft: int
    - has_gym, has_pool, has_parking: binary (0 or 1)
    
    Returns: Estimated price in Rupees
    """
    try:
        le = joblib.load('locality_encoder.pkl')
        model = joblib.load('price_prediction_model.pkl')
        
        # Encode locality
        if locality not in le.classes_:
            # Use average if unseen locality
            locality_encoded = np.mean(le.transform(le.classes_))
        else:
            locality_encoded = le.transform([locality])[0]
        
        input_data = np.array([[locality_encoded, bhk, sqft, has_gym, has_pool, has_parking]])
        predicted_price = model.predict(input_data)[0]
        
        return round(predicted_price)
    
    except Exception as e:
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    print("\n=== Example Predictions ===")
    
    examples = [
        ("Kondapur", 2, 1100, 1, 0, 1),
        ("Madhapur", 3, 1450, 1, 1, 1),
        ("Gachibowli", 2, 1050, 0, 0, 1),
        ("Kompally", 2, 950, 0, 0, 0),
    ]
    
    for loc, bhk, sqft, gym, pool, park in examples:
        price = predict_price(loc, bhk, sqft, gym, pool, park)
        print(f"{loc} | {bhk}BHK | {sqft} sqft → ₹{price:,.0f}")
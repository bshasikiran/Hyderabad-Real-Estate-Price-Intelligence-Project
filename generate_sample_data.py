"""
Sample Data Generator for Hyderabad Real Estate Project
Creates realistic data mimicking 99acres listings for localities like Kondapur, Madhapur, Gachibowli etc.
Use this when live scraping is blocked (very common).
"""

import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

localities = [
    'Kondapur', 'Madhapur', 'Gachibowli', 'Hitec City', 'Jubilee Hills',
    'Banjara Hills', 'Kukatpally', 'Miyapur', 'Nizampet', 'Kompally',
    'Uppal', 'LB Nagar', 'Secunderabad', 'Begumpet', 'Ameerpet'
]

def generate_realistic_data(n=450):
    data = []
    
    for _ in range(n):
        locality = random.choice(localities)
        
        # BHK distribution (realistic)
        bhk = np.random.choice([1, 2, 3, 4], p=[0.15, 0.45, 0.30, 0.10])
        
        # Area based on BHK
        if bhk == 1:
            sqft = np.random.randint(550, 850)
        elif bhk == 2:
            sqft = np.random.randint(900, 1350)
        elif bhk == 3:
            sqft = np.random.randint(1300, 1900)
        else:
            sqft = np.random.randint(1800, 2800)
        
        # Base price per sqft (varies significantly by locality)
        base_ppsqft = {
            'Kondapur': 8500, 'Madhapur': 9200, 'Gachibowli': 7800,
            'Hitec City': 9500, 'Jubilee Hills': 12500, 'Banjara Hills': 11500,
            'Kukatpally': 6200, 'Miyapur': 5800, 'Nizampet': 5500,
            'Kompally': 5100, 'Uppal': 4800, 'LB Nagar': 5200,
            'Secunderabad': 7100, 'Begumpet': 6800, 'Ameerpet': 6500
        }[locality]
        
        # Add noise and premium factors
        price_per_sqft = base_ppsqft + np.random.normal(0, 1200)
        
        # Gated community premium (~8-12%)
        is_gated = random.random() > 0.35
        if is_gated:
            price_per_sqft *= 1.09
        
        # Amenities effect
        has_gym = 1 if random.random() > 0.4 else 0
        has_pool = 1 if random.random() > 0.55 else 0
        has_parking = 1 if random.random() > 0.25 else 0
        
        if has_gym:
            price_per_sqft += 350
        if has_pool:
            price_per_sqft += 420
        if has_parking:
            price_per_sqft += 180
        
        price = int(price_per_sqft * sqft)
        
        # Round price to look realistic
        if price > 15000000:  # > 1.5 Cr
            price = round(price / 100000) * 100000
        else:
            price = round(price / 10000) * 10000
        
        data.append({
            'locality': locality,
            'price': price,
            'bhk': bhk,
            'sqft': sqft,
            'price_per_sqft': round(price / sqft, 2),
            'has_gym': has_gym,
            'has_pool': has_pool,
            'has_parking': has_parking,
            'has_clubhouse': 1 if random.random() > 0.5 else 0,
            'has_security': 1 if random.random() > 0.3 else 0,
            'is_gated': 1 if is_gated else 0
        })
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_realistic_data(450)
    df.to_csv('hyderabad_properties.csv', index=False)
    print("Sample dataset created: hyderabad_properties.csv")
    print(f"Total rows: {len(df)}")
    print("\nSample localities distribution:")
    print(df['locality'].value_counts().head(8))
    print("\nPrice per sqft stats:")
    print(df['price_per_sqft'].describe())
"""
Step 2 & 3: Data Cleaning + EDA for Hyderabad Real Estate
Run after generating hyderabad_properties.csv
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder

# Load data
df = pd.read_csv('hyderabad_properties.csv')
print("Initial shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head())

# === DATA CLEANING ===
print("\n=== Cleaning Data ===")

# Remove rows with missing critical values
df = df.dropna(subset=['locality', 'price', 'bhk', 'sqft'])

# Filter unrealistic values
df = df[(df['price'] > 1000000) & (df['price'] < 50000000)]  # 10L to 5Cr
df = df[(df['sqft'] > 400) & (df['sqft'] < 4000)]
df = df[df['bhk'].between(1, 5)]

# Create derived columns if not present
if 'price_per_sqft' not in df.columns:
    df['price_per_sqft'] = df['price'] / df['sqft']

# Standardize locality names
df['locality'] = df['locality'].str.strip().str.title()

print(f"Cleaned dataset shape: {df.shape}")

# Save cleaned version
df.to_csv('hyderabad_properties_cleaned.csv', index=False)
print("Cleaned data saved to hyderabad_properties_cleaned.csv")

# === EDA CHARTS ===
print("\n=== Generating EDA Charts ===")

plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Chart 1: Box plot - Price per sqft by Locality (Top 8)
top_localities = df['locality'].value_counts().head(8).index
df_top = df[df['locality'].isin(top_localities)]

sns.boxplot(data=df_top, x='locality', y='price_per_sqft', ax=axes[0,0], palette='Set2')
axes[0,0].set_title('Price per Sqft Distribution by Locality (Top 8)', fontsize=14, fontweight='bold')
axes[0,0].tick_params(axis='x', rotation=45)
axes[0,0].set_ylabel('Price per Sqft (₹)')

# Chart 2: Scatter plot - Area vs Price colored by BHK
scatter = axes[0,1].scatter(df['sqft'], df['price'], c=df['bhk'], cmap='viridis', alpha=0.6, s=60)
axes[0,1].set_title('Price vs Area by BHK Configuration', fontsize=14, fontweight='bold')
axes[0,1].set_xlabel('Area (Sqft)')
axes[0,1].set_ylabel('Price (₹)')
plt.colorbar(scatter, ax=axes[0,1], label='BHK')

# Chart 3: Correlation Heatmap
numeric_cols = ['price', 'sqft', 'bhk', 'price_per_sqft', 'has_gym', 'has_pool', 'has_parking']
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=axes[1,0])
axes[1,0].set_title('Correlation Heatmap', fontsize=14, fontweight='bold')

# Chart 4: Average price per sqft by locality (bar)
avg_ppsqft = df.groupby('locality')['price_per_sqft'].mean().sort_values(ascending=False).head(10)
avg_ppsqft.plot(kind='bar', ax=axes[1,1], color='teal')
axes[1,1].set_title('Average Price per Sqft by Locality (Top 10)', fontsize=14, fontweight='bold')
axes[1,1].tick_params(axis='x', rotation=45)
axes[1,1].set_ylabel('Avg Price/Sqft (₹)')

plt.tight_layout()
plt.savefig('hyderabad_eda_charts.png', dpi=300, bbox_inches='tight')
print("EDA charts saved as hyderabad_eda_charts.png")

# Print key business insights
print("\n=== Key Business Insights ===")
print("\nTop 5 Localities by Avg Price/Sqft:")
print(df.groupby('locality')['price_per_sqft'].mean().sort_values(ascending=False).head(5))

print("\nGated Community Premium:")
gated = df[df.get('is_gated', 0) == 1]['price_per_sqft'].mean()
non_gated = df[df.get('is_gated', 0) == 0]['price_per_sqft'].mean()
print(f"Gated: ₹{gated:,.0f} | Non-Gated: ₹{non_gated:,.0f} | Premium: {((gated-non_gated)/non_gated)*100:.1f}%")

print("\nBest Value Localities (lowest price/sqft):")
print(df.groupby('locality')['price_per_sqft'].mean().sort_values().head(5))
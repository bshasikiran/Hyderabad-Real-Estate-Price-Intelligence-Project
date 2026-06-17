"""
Step 5: Streamlit App for Hyderabad Real Estate Price Intelligence
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Hyderabad Real Estate Intelligence", layout="wide")

# Load data and model
@st.cache_data
def load_data():
    return pd.read_csv('hyderabad_properties_cleaned.csv')

@st.cache_resource
def load_model():
    model = joblib.load('price_prediction_model.pkl')
    le = joblib.load('locality_encoder.pkl')
    return model, le

df = load_data()
model, le = load_model()

st.title("🏠 Hyderabad Real Estate Price Intelligence")
st.markdown("**Live scraped + ML-powered insights for Hyderabad property market**")

# Sidebar
st.sidebar.header("Navigation")
tab = st.sidebar.radio("Choose Tab", ["Price Estimator", "Market Insights", "Data Explorer"])

if tab == "Price Estimator":
    st.header("💰 Fair Price Estimator")
    st.markdown("Get instant price estimate for any property")
    
    col1, col2 = st.columns(2)
    
    with col1:
        locality = st.selectbox("Locality", sorted(df['locality'].unique()))
        bhk = st.selectbox("BHK", [1, 2, 3, 4])
        sqft = st.slider("Built-up Area (sqft)", 500, 3000, 1100, step=50)
    
    with col2:
        has_gym = st.checkbox("Has Gym", value=True)
        has_pool = st.checkbox("Has Swimming Pool")
        has_parking = st.checkbox("Has Parking", value=True)
    
    if st.button("Predict Price", type="primary"):
        # Prepare input
        locality_encoded = le.transform([locality])[0] if locality in le.classes_ else 0
        
        input_data = [[locality_encoded, bhk, sqft, 
                       int(has_gym), int(has_pool), int(has_parking)]]
        
        predicted_price = model.predict(input_data)[0]
        
        st.success(f"**Estimated Fair Price: ₹{predicted_price:,.0f}**")
        
        # Show range
        lower = predicted_price * 0.92
        upper = predicted_price * 1.08
        st.info(f"Reasonable negotiation range: ₹{lower:,.0f} – ₹{upper:,.0f}")
        
        # Per sqft
        ppsqft = predicted_price / sqft
        st.write(f"Price per sqft: **₹{ppsqft:,.0f}**")

elif tab == "Market Insights":
    st.header("📊 Market Insights")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Listings", len(df))
    col2.metric("Avg Price/Sqft", f"₹{df['price_per_sqft'].mean():,.0f}")
    col3.metric("Most Expensive Area", df.groupby('locality')['price_per_sqft'].mean().idxmax())
    col4.metric("Best Value Area", df.groupby('locality')['price_per_sqft'].mean().idxmin())
    
    st.divider()
    
    # Insights
    st.subheader("Which locality gives the best price per sqft value?")
    avg_ppsqft = df.groupby('locality')['price_per_sqft'].mean().sort_values()
    st.bar_chart(avg_ppsqft)
    
    st.subheader("Does gated community add price premium?")
    if 'is_gated' in df.columns:
        gated_avg = df[df['is_gated'] == 1]['price_per_sqft'].mean()
        non_gated_avg = df[df['is_gated'] == 0]['price_per_sqft'].mean()
        premium = ((gated_avg - non_gated_avg) / non_gated_avg) * 100
        
        st.write(f"**Gated communities command ~{premium:.1f}% premium**")
        st.write(f"Gated: ₹{gated_avg:,.0f}/sqft | Non-Gated: ₹{non_gated_avg:,.0f}/sqft")
    
    st.subheader("Fair price examples (2BHK)")
    examples = df[df['bhk'] == 2].groupby('locality')['price'].mean().sort_values().head(6)
    st.dataframe(examples.reset_index().rename(columns={'price': 'Avg 2BHK Price'}))

else:  # Data Explorer
    st.header("🔍 Data Explorer")
    st.dataframe(df.head(20))
    
    st.subheader("Filter Data")
    selected_locality = st.multiselect("Select Localities", df['locality'].unique())
    if selected_locality:
        filtered = df[df['locality'].isin(selected_locality)]
        st.dataframe(filtered)

st.sidebar.markdown("---")
st.sidebar.caption("Built with ❤️ | Scraped + ML Pipeline | 2026")
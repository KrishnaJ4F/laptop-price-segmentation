import streamlit as st
import pandas as pd
import numpy as np
import joblib
import base64
import os

# Page Config
st.set_page_config(page_title="PrediLap | Laptop Price Analytics", page_icon="💻", layout="wide")

# Helper for Background Image
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    page_bg_img = '''
    <style>
    .stApp {
        background-image: url("data:image/png;base64,%s");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Overlay for readability */
    .stApp::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%%;
        height: 100%%;
        background: rgba(255, 255, 255, 0.6); /* Soft white overlay */
        backdrop-filter: blur(2px);
        z-index: -1;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set Background (Bluemora Style)
bg_path = r"Image/bluemora_bg_1767704478553.png"
if os.path.exists(bg_path):
    set_png_as_page_bg(bg_path)

# Custom CSS for Premium UI/UX (Bluemora Inspired)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=Inter:wght@300;400;500;600&display=swap');

    :root {
        --primary: #c9a07c;
        --bg-white: rgba(255, 255, 255, 0.98);
        --text-deep: #1a1816;
        --text-muted: #3a352f; /* Darkened further for readability */
        --accent-line: #ece8e1;
        --glass-bg: rgba(255, 255, 255, 0.96);
    }

    /* Global Transitions */
    * { transition: all 0.2s ease-in-out; }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Elegant Navigation Header */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 0;
        border-bottom: 2px solid var(--text-deep);
        margin-bottom: 60px;
    }
    
    .nav-logo {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-deep);
        letter-spacing: -0.5px;
    }

    /* Headlines */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
        color: var(--text-deep) !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }
    
    .main-title {
        font-size: 4rem !important;
        text-align: center;
        margin-bottom: 1rem !important;
        color: var(--text-deep) !important;
    }
    
    .sub-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 1.25rem !important;
        text-align: center;
        color: var(--text-deep) !important;
        font-weight: 400 !important;
        max-width: 850px;
        letter-spacing: 0.3px;
        line-height: 1.7;
        margin: 0 auto 80px auto !important;
    }

    /* Target the Unified Main Container */
    [data-testid="stMainBlockContainer"] {
        background: var(--glass-bg);
        border: 1px solid var(--accent-line);
        padding: 80px 60px !important;
        border-radius: 8px;
        margin-top: 40px !important;
        max-width: 1300px !important;
        backdrop-filter: blur(25px);
        box-shadow: 0 40px 100px rgba(0,0,0,0.08);
    }

    /* Section Containers */
    div.stVerticalBlock > div > div[data-testid="stVerticalBlock"] {
        background: var(--bg-white);
        border: 1px solid var(--accent-line);
        padding: 40px;
        border-radius: 4px;
        margin-bottom: 40px;
        backdrop-filter: blur(10px);
    }

    /* Input Styling */
    .stSelectbox label, .stSlider label {
        color: var(--text-deep) !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 1.2px;
        margin-bottom: 10px !important;
    }

    /* Button Styling */
    .stButton>button {
        background-color: var(--text-deep) !important;
        color: white !important;
        border: none !important;
        padding: 16px 40px !important;
        border-radius: 0 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        width: auto !important;
        display: block !important;
        margin: 40px auto !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1) !important;
    }

    .stButton>button:hover {
        background-color: var(--primary) !important;
        transform: translateY(-2px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2) !important;
    }

    /* Result Display Refinement */
    .prediction-box {
        background: rgba(255, 255, 255, 0.9);
        border: 1px solid var(--accent-line);
        padding: 60px 40px;
        border-radius: 4px;
        text-align: center;
        margin: 40px auto;
        max-width: 900px;
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.03);
    }

    .prediction-label {
        text-transform: uppercase;
        letter-spacing: 5px;
        font-size: 0.85rem;
        color: var(--text-muted);
        margin-bottom: 15px;
        font-weight: 500;
    }

    .prediction-text {
        font-family: 'Playfair Display', serif;
        font-size: 6rem !important;
        color: var(--text-deep) !important;
        font-weight: 800;
        margin: 20px 0;
        line-height: 1;
        letter-spacing: -2px;
    }

    .prediction-accent {
        height: 3px;
        width: 60px;
        background: var(--primary);
        margin: 25px auto 0;
    /* Results & Cards */
    .info-card {
        padding: 40px;
        background: white;
        border: 1px solid var(--accent-line);
        height: 100%;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02);
    }

    hr {
        border: 0;
        height: 1px;
        background-color: var(--accent-line);
        margin: 60px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Load Artifacts
@st.cache_resource
def load_assets():
    model = joblib.load('laptop_model.pkl')
    scaler = joblib.load('laptop_scaler.pkl')
    encoders = joblib.load('laptop_encoders.pkl')
    df = pd.read_csv('data/laptop_cleaned.csv')
    return model, scaler, encoders, df

try:
    model, scaler, encoders, df = load_assets()
except Exception as e:
    st.error(f"Error loading assets: {e}")
    st.stop()

# Helper to get unique valid values from dataset
def get_valid_options(brand, column):
    if brand == "All":
        return sorted(df[column].unique().tolist())
    return sorted(df[df['Brand'] == brand][column].unique().tolist())

# Header
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">Laptop Market Analysis</div>
    <div style="display:flex; gap:30px; font-size:0.8rem; letter-spacing:1px; text-transform:uppercase; color:#6b635b;">
        <span>Analytics</span>
        <span>Market Insights</span>
        <span>Segments</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">Intelligence starts with the right analysis.</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Discover the precise market segment for any laptop configuration. Data-driven insights powered by advanced machine learning.</p>', unsafe_allow_html=True)

# Main Interface
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown('<p class="prediction-label" style="text-align:left; letter-spacing:2px; margin-bottom:20px;">🛠️ Core Configuration</p>', unsafe_allow_html=True)
    
    # 1. Brand Selection (Triggers dependency)
    available_brands = sorted(df['Brand'].unique().tolist())
    brand = st.selectbox("Select Brand", available_brands, index=0)
    
    # Dynamic Filtering based on Brand
    brand_df = df[df['Brand'] == brand]
    
    # 2. Dependent Fields
    col_a, col_b = st.columns(2)
    with col_a:
        series_options = sorted(brand_df['Series'].dropna().unique().tolist())
        if not series_options: series_options = ["Standard"]
        series = st.selectbox("Series", series_options)
        
        os_options = sorted(brand_df['OS'].dropna().unique().tolist())
        os_type = st.selectbox("Operating System", os_options)
        
    with col_b:
        cpu_options = sorted(brand_df['CPU'].dropna().unique().tolist())
        cpu = st.selectbox("Processor (CPU)", cpu_options)
        
        gpu_options = sorted(brand_df['GPU'].fillna("Integrated Graphics").unique().tolist())
        gpu = st.selectbox("Graphics (GPU)", gpu_options)

    st.markdown('<p class="prediction-label" style="text-align:left; letter-spacing:2px; margin-top:30px; margin-bottom:20px;">📊 User Perception</p>', unsafe_allow_html=True)
    rating = st.slider("User Rating (out of 5.0)", 1.0, 5.0, 4.2, 0.1)

with col2:
    st.markdown('<p class="prediction-label" style="text-align:left; letter-spacing:2px; margin-bottom:20px;">⚙️ Technical Specs</p>', unsafe_allow_html=True)
    
    # Constraints based on Brand
    def get_range(col):
        vals = brand_df[col].dropna()
        if vals.empty: return 0.0, 10.0, 1.5
        return float(vals.min()), float(vals.max()), float(vals.median())

    # RAM
    ram_options = sorted(brand_df['RAM_GB'].unique().tolist())
    ram = st.select_slider("RAM Capacity (GB)", options=ram_options, value=ram_options[len(ram_options)//2])
    
    # Storage
    storage_options = sorted(brand_df['Storage_GB'].unique().tolist())
    storage = st.select_slider("Storage Capacity (GB)", options=storage_options, value=storage_options[len(storage_options)//2])
    
    # Display
    disp_min, disp_max, disp_med = get_range('Display_inches')
    display = st.slider("Display Size (Inches)", disp_min, disp_max, disp_med, 0.1)
    
    # Weight
    weight_min, weight_max, weight_med = get_range('Weight_KG')
    weight = st.slider("Weight (KG)", weight_min, weight_max, weight_med, 0.01)

# Container remains open for results
st.markdown('<br>', unsafe_allow_html=True)
# Prediction Logic
if st.button("🔮 ANALYZE MARKET SEGMENT"):
    # Safe Transform helper
    def safe_transform(col, val):
        try:
            return encoders[col].transform([str(val)])[0]
        except:
            # Handle unseen labels by finding closest match or defaulting to 0
            return 0

    # Preprocess inputs
    input_data = pd.DataFrame([[
        safe_transform('Brand', brand),
        safe_transform('Series', series),
        safe_transform('CPU', cpu),
        safe_transform('GPU', gpu if gpu != "Integrated Graphics" else ""),
        safe_transform('OS', os_type),
        ram,
        storage,
        display,
        weight,
        rating
    ]], columns=['Brand', 'Series', 'CPU', 'GPU', 'OS', 'RAM_GB', 'Storage_GB', 'Display_inches', 'Weight_KG', 'Rating'])
    
    # Ensure column order matches training FEATURES
    input_data = input_data[['Brand', 'Series', 'CPU', 'GPU', 'OS', 'RAM_GB', 'Storage_GB', 'Display_inches', 'Weight_KG', 'Rating']]
    
    scaled_input = scaler.transform(input_data)
    prediction = model.predict(scaled_input)
    predicted_class = encoders['Price_Category'].inverse_transform(prediction)[0]
    
    # Result Display
    st.markdown(f"""
        <div class="prediction-box">
            <p class="prediction-label">Suggested Market Segment</p>
            <p class="prediction-text">{predicted_class}</p>
            <div class="prediction-accent"></div>
        </div>
    """, unsafe_allow_html=True)

    # Detailed Insights with Images
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f'<h3 style="text-align:center; margin-bottom:50px;">{predicted_class} Segment Analysis</h3>', unsafe_allow_html=True)
    
    # Dynamic Image Selection based on Brand, Series, and Segment
    brand_lower = brand.lower()
    series_lower = series.lower()
    
    img_path = ""
    # 1. Check for Apple
    if 'apple' in brand_lower:
        img_path = r"Image/laptop_apple_style_1767704508837.png"
    # 2. Check for Gaming
    elif any(x in brand_lower or x in series_lower for x in ['gaming', 'msi', 'rog', 'tuf', 'legion', 'alienware', 'nitro', 'predator', 'loq', 'victus']):
        img_path = r"Image/laptop_gaming_style_1767704537301.png"
    # 3. Check for Business/Premium
    elif any(x in series_lower for x in ['thinkpad', 'latitude', 'xps', 'elitebook', 'zenbook', 'surface', 'macbook', 'spectre', 'envy', 'adamo']):
        img_path = r"Image/laptop_business_style_1767704577670.png"
    # 4. Fallback to Segment based logic if above don't catch specific "vibe"
    else:
        if predicted_class == 'Premium':
            img_path = r"Image/laptop_premium_segment_1767703818836.png"
        elif predicted_class == 'High':
            img_path = r"Image/laptop_high_segment_1767703858769.png"
        elif predicted_class == 'Medium':
            img_path = r"Image/laptop_medium_segment_1767703883684.png"
        else:
            img_path = r"Image/laptop_low_segment_1767703911249.png"

    # Last Fallback
    if not img_path or not os.path.exists(img_path):
        img_path = r"Image/laptop_generic_sleek_1767704614725.png"

    description = ""
    if predicted_class == 'Premium':
        description = "Targeted at power users, creative professionals, and high-end gamers. Features top-tier build quality, premium materials, and cutting-edge performance tech. This segment represents the pinnacle of laptop engineering."
    elif predicted_class == 'High':
        description = "Robust performance for corporate and professional workloads. Excellent balance of speed, durability, and aesthetics. Perfect for high-intensity multitasking and modern office environments."
    elif predicted_class == 'Medium':
        description = "The sweet spot for students and general home office use. Reliable multitasking, decent battery life, and a versatile design that fits perfectly into lifestyle-oriented settings."
    elif predicted_class == 'Low':
        description = "Essential specifications focused on high value and core tasks like web browsing, document editing, and content consumption. Ideal for entry-level users and educational needs."

    ins_col1, ins_col2 = st.columns([1, 1], gap="large")
    with ins_col1:
        if img_path:
            st.image(img_path, use_container_width=True)
    with ins_col2:
        st.markdown(f"""
            <div class="info-card">
                <h4 style="margin-top:0; color:#c9a07c; font-family:'Playfair Display', serif; font-size:1.8rem;">{predicted_class} Excellence</h4>
                <p style="font-size:1.1rem; line-height:1.8; color:#6b635b;">{description}</p>
                <hr style="margin: 30px 0;">
                <p style="font-weight: 600; color: #1a1816; text-transform:uppercase; letter-spacing:1px; font-size:0.8rem;">Core Value Proposition</p>
                <ul style="color: #6b635b; font-size:1rem; line-height:2;">
                    <li>High Market Relevance</li>
                    <li>Balanced Price-to-Performance</li>
                    <li>Optimal Material Selection</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

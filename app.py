import streamlit as st
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import os
from datetime import datetime
from fpdf import FPDF
import base64

# Set page config
st.set_page_config(page_title="PlasmoDetect", page_icon="🧬", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Card styling */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    
    /* Result containers */
    .result-parasitized {
        background: linear-gradient(135deg, #feb692 0%, #ea5455 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
        animation: pulse 2s infinite;
    }
    
    .result-uninfected {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    /* Confidence meter */
    .confidence-meter {
        background: #f0f2f6;
        border-radius: 10px;
        height: 30px;
        margin: 1rem 0;
        position: relative;
    }
    
    .confidence-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 10px;
        height: 100%;
        transition: width 0.5s ease-in-out;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Language selector */
    .language-selector {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    
    /* Image container */
    .image-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 0.5rem 1rem;
        background-color: transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Load model
model = load_model("my_model_malaria.h5")

# Languages
translations = {
    "en": {
        "title": "🧬 PlasmoDetect: Malaria Detection & Report",
        "subtitle": "AI-Powered Malaria Diagnosis System",
        "upload": "Upload a blood smear image",
        "sample": "Or choose a sample image",
        "confidence": "Model Confidence",
        "prediction": "Prediction",
        "generate_report": "Generate Medical Report",
        "download_report": "📄 Download Report",
        "about": "About Malaria",
        "model_info": "Model Info",
        "patient_info": "Patient Information",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "symptoms": "Symptoms",
        "doctor_note": "Doctor's Note",
        "about_text": "Malaria is a life-threatening disease caused by parasites transmitted through the bites of infected mosquitoes.",
        "symptoms_list": "Common Symptoms: Fever, chills, headache, nausea, vomiting, fatigue",
        "accuracy": "Model Accuracy: 95%",
        "disclaimer": "⚠️ This is an AI-assisted diagnostic tool. Please consult a healthcare professional for confirmation.",
        "analyze": "🔬 Analyze Image",
        "processing": "Processing image...",
        "result_parasitized": "⚠️ PARASITIZED DETECTED",
        "result_uninfected": "✅ UNINFECTED",
        "sample_images": "Sample Images"
    },
    "Am": {
        "title": "🧬 ፕላዝሞ ዲቴክት፡ የወባ ማወቂያ እና ሪፖርት",
        "subtitle": "በአይ የተደገፈ የወባ መመርመሪያ ሲስተም",
        "upload": "የደም ስሚር ምስል ይጫኑ",
        "sample": "ወይም የናሙና ምስል ይምረጡ",
        "confidence": "የሞዴል እርግጠኛነት",
        "prediction": "ትንበያ",
        "generate_report": "የህክምና ሪፖርት ይፍጠሩ",
        "download_report": "📄 ሪፖርቱን ያውርዱ",
        "about": "ስለ ወባ",
        "model_info": "የሞዴል መረጃ",
        "patient_info": "የታካሚ መረጃ",
        "name": "ስም",
        "age": "ዕድሜ",
        "gender": "ፆታ",
        "symptoms": "ምልክቶች",
        "doctor_note": "የዶክተር ማስታወሻ",
        "about_text": "ወባ በተያዙ ትንኞች ንክሻ በሚተላለፉ ጥገኛ ተውሳኮች የሚመጣ ለሕይወት አስጊ የሆነ በሽታ ነው።",
        "symptoms_list": "የተለመዱ ምልክቶች፡ ትኩሳት፣ ብርድ ብርድ ማለት፣ ራስ ምታት፣ ማቅለሽለሽ፣ ማስታወክ፣ ድካም",
        "accuracy": "የሞዴል ትክክለኛነት፡ 95%",
        "disclaimer": "⚠️ ይህ በአይ የታገዘ የምርመራ መሳሪያ ነው። እባክዎ ለማረጋገጫ የሙዚቃ ባለሙያን ያማክሩ።",
        "analyze": "🔬 ምስሉን መርምር",
        "processing": "ምስሉ በመተንተን ላይ...",
        "result_parasitized": "⚠️ በሽታ አምጪ ተህዋሲያን ተገኝተዋል",
        "result_uninfected": "✅ በሽታ አምጪ ተህዋሲያን አልተገኙም",
        "sample_images": "የናሙና ምስሎች"
    }
}

# Language Selector with Labels
language_options = {"English": "en", "Amharic": "Am"}
selected_lang_label = st.sidebar.selectbox("🌐 Language / ቋንቋ", list(language_options.keys()))
lang = language_options[selected_lang_label]
t = translations[lang]

# Main Header
st.markdown(f"""
<div class="main-header">
    <h1>{t['title']}</h1>
    <p style="font-size: 1.2rem; opacity: 0.9;">{t['subtitle']}</p>
</div>
""", unsafe_allow_html=True)

# Disclaimer
st.info(t['disclaimer'])

# Create columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    # Image Input Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📸 " + t['upload'])
    
    uploaded_file = st.file_uploader(t["upload"], type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(image, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"### {t['sample_images']}")
        try:
            sample_images = os.listdir("samples")
            if sample_images:
                cols = st.columns(3)
                for idx, sample in enumerate(sample_images[:3]):  # Show first 3 samples
                    with cols[idx]:
                        st.image(f"samples/{sample}", use_container_width=True)
                        if st.button(f"Use {sample}", key=f"sample_{idx}"):
                            image = Image.open(f"samples/{sample}")
        except:
            st.info("No sample images found in 'samples' folder")
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Patient Info Section
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👤 " + t['patient_info'])
    
    name = st.text_input(t["name"], placeholder="John Doe")
    age = st.number_input(t["age"], min_value=0, max_value=120, value=30)
    gender = st.selectbox(t["gender"], ["Male", "Female", "Other"])
    symptoms = st.text_area(t["symptoms"], placeholder="Fever, chills, headache...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Model Info Card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🤖 " + t['model_info'])
    st.markdown(f"""
    - **Model:** CNN Architecture
    - **Input Size:** 64x64 pixels
    - **Accuracy:** {t['accuracy']}
    - **Training Data:** Kaggle Malaria Dataset
    """)
    st.markdown('</div>', unsafe_allow_html=True)

# Prediction function
def predict(img):
    img_resized = img.resize((64, 64))
    img_array = np.array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prob = model.predict(img_array)[0][0]
    label = "Uninfected" if prob > 0.5 else "Parasitized"
    confidence = round(float(prob if label == "Uninfected" else 1 - prob) * 100, 2)
    return label, confidence

# Analysis Section
if image:
    st.markdown("---")
    
    # Analysis button
    if st.button(t['analyze'], use_container_width=True):
        with st.spinner(t['processing']):
            result, confidence = predict(image)
        
        # Display result with styling
        if result == "Parasitized":
            st.markdown(f"""
            <div class="result-parasitized">
                <h2>{t['result_parasitized']}</h2>
                <p style="font-size: 1.2rem;">{t['prediction']}: {result}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-uninfected">
                <h2>{t['result_uninfected']}</h2>
                <p style="font-size: 1.2rem;">{t['prediction']}: {result}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Confidence meter
        st.markdown(f"### {t['confidence']}")
        st.markdown(f"""
        <div class="confidence-meter">
            <div class="confidence-fill" style="width: {confidence}%;"></div>
        </div>
        <p style="text-align: center; font-weight: bold;">{confidence}%</p>
        """, unsafe_allow_html=True)
        
        # Doctor's note
        st.markdown(f"""
        <div class="info-box">
            <strong>{t['doctor_note']}:</strong> This image appears {result.lower()}. 
            Please consult a doctor for proper diagnosis and treatment.
        </div>
        """, unsafe_allow_html=True)
        
        # PDF Generator (keep your existing PDF generation code)
        def generate_pdf(image, result, confidence):
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 20)
            pdf.set_text_color(30, 30, 120)
            pdf.cell(200, 10, "PlasmoDetect Medical Report", ln=True, align='C')
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", size=12)
            pdf.ln(5)
            
            pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "Patient Information", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, f"Name: {name}", ln=True)
            pdf.cell(200, 8, f"Age: {age}    Gender: {gender}", ln=True)
            pdf.multi_cell(0, 8, f"Symptoms: {symptoms}")
            pdf.ln(5)
            
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(200, 10, "Diagnostic Result", ln=True)
            pdf.set_font("Arial", size=12)
            
            if result == "Parasitized":
                pdf.set_text_color(220, 20, 60)
            else:
                pdf.set_text_color(34, 139, 34)
            
            pdf.cell(200, 10, f"Result: {result}", ln=True)
            pdf.cell(200, 10, f"Model Confidence: {confidence}%", ln=True)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
            
            pdf.set_font("Arial", 'I', 11)
            pdf.multi_cell(0, 8, f"Doctor's Note: This blood smear appears {result.lower()} based on AI analysis. It is advised to consult a certified medical professional for further diagnosis and confirmation.")
            pdf.ln(5)
            
            img_path = "temp_image.jpg"
            image.save(img_path)
            pdf.image(img_path, x=55, y=140, w=100)
            pdf.ln(85)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(200, 10, "________________________", ln=True, align='R')
            pdf.cell(200, 6, "Doctor's Signature", ln=True, align='R')
            
            pdf.output("malaria_report.pdf")
            return "malaria_report.pdf"
        
        # Generate report button
        if st.button(t["generate_report"], use_container_width=True):
            pdf_path = generate_pdf(image, result, confidence)
            with open(pdf_path, "rb") as f:
                st.download_button(
                    t["download_report"], 
                    f, 
                    file_name="malaria_report.pdf",
                    use_container_width=True
                )

# About Section
with st.expander(t["about"]):
    col1, col2 = st.columns(2)
    with col1:
        st.write(t["about_text"])
        st.markdown(f"**{t['symptoms_list']}**")
    with col2:
        st.image("https://www.cdc.gov/malaria/images/malaria-life-cycle.jpg", 
                caption="Malaria Life Cycle", use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray; padding: 1rem;">
    <p>© 2026 By Addisu Amare PlasmoDetect - AI-Powered Malaria Detection System</p>
    <p style="font-size: 0.8rem;">For research and educational purposes only</p>
</div>
""", unsafe_allow_html=True)
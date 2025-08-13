# burn_app.py
import streamlit as st
from datetime import datetime, timedelta
from burn_ai_estimator import BurnEstimator, PatientInfo, InjuryContext

st.set_page_config(page_title="Burn %TBSA & Fluid Estimator", layout="wide")

st.title("🔥 AI-Based Burn %TBSA & Fluid Estimator")

# --- Patient Data ---
st.header("Patient Information")
col1, col2, col3 = st.columns(3)
age = col1.number_input("Age (years)", min_value=0, step=1, value=30)
weight = col2.number_input("Weight (kg)", min_value=1.0, step=0.5, value=70.0)
sex = col3.selectbox("Sex", ["M", "F", "Other"])
height = col1.number_input("Height (cm)", min_value=30.0, step=0.5, value=170.0)

# --- Injury Time ---
st.header("Injury Context")
hours_since = st.slider("Hours since burn", min_value=0.0, max_value=24.0, step=0.5, value=2.0)
injury_time = datetime.utcnow() - timedelta(hours=hours_since)
fluids_given = st.number_input("Fluids given so far (mL)", min_value=0.0, step=100.0, value=0.0)

# --- Image Uploads ---
st.header("Burn Images")
burn_img_file = st.file_uploader("Upload Burn Image", type=["jpg", "jpeg", "png"])
palm_img_file = st.file_uploader("Upload Palm Image (optional)", type=["jpg", "jpeg", "png"])

# Options
use_palmar = st.checkbox("Use Palmar Method", value=True)
formula = st.radio("Resuscitation formula", ["Parkland", "Modified Brooke"])

if st.button("Estimate") and burn_img_file is not None:
    with open("temp_burn.jpg", "wb") as f:
        f.write(burn_img_file.getbuffer())

    palm_path = None
    if palm_img_file:
        with open("temp_palm.jpg", "wb") as f:
            f.write(palm_img_file.getbuffer())
        palm_path = "temp_palm.jpg"

    estimator = BurnEstimator()
    patient_info = PatientInfo(age_years=age, weight_kg=weight, sex=sex, height_cm=height)
    injury_ctx = InjuryContext(time_of_burn=injury_time, fluids_given_ml=fluids_given)

    results = estimator.estimate(
        patient=patient_info,
        injury=injury_ctx,
        burn_image_path="temp_burn.jpg",
        palm_image_path=palm_path,
        use_palmar=use_palmar,
        use_parkland=(formula == "Parkland")
    )

    st.subheader("Results")
    st.write(f"**TBSA %**: {results['tbsa_percent']}% ({results['tbsa_method']})")
    st.write(f"**Burn area (pixels)**: {results['burn_area_pixels']}")
    if results['palm_area_pixels']:
        st.write(f"**Palm area (pixels)**: {results['palm_area_pixels']}")

    st.subheader("Fluid Plan")
    fluid_plan = results['fluid_plan']
    st.json(fluid_plan)

    st.warning("\n".join(results['notes']))

else:
    st.info("Please upload at least a burn image to start estimation.")

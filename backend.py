# backend.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from burn_ai_estimator import BurnEstimator, PatientInfo, InjuryContext
from datetime import datetime, timedelta
import shutil
import os

app = FastAPI()
estimator = BurnEstimator()

@app.post("/estimate")
async def estimate(
    age: float = Form(...),
    weight: float = Form(...),
    sex: str = Form(...),
    height: float = Form(...),
    hours_since: float = Form(...),
    fluids_given: float = Form(...),
    use_palmar: bool = Form(...),
    formula: str = Form(...),
    burn_image: UploadFile = None,
    palm_image: UploadFile = None
):
    burn_path = "temp_burn.jpg"
    palm_path = None

    with open(burn_path, "wb") as f:
        shutil.copyfileobj(burn_image.file, f)

    if palm_image:
        palm_path = "temp_palm.jpg"
        with open(palm_path, "wb") as f:
            shutil.copyfileobj(palm_image.file, f)

    patient = PatientInfo(age_years=age, weight_kg=weight, sex=sex, height_cm=height)
    injury = InjuryContext(time_of_burn=datetime.utcnow()-timedelta(hours=hours_since),
                           fluids_given_ml=fluids_given)

    result = estimator.estimate(
        patient=patient,
        injury=injury,
        burn_image_path=burn_path,
        palm_image_path=palm_path,
        use_palmar=use_palmar,
        use_parkland=(formula == "Parkland")
    )
    return JSONResponse(result)

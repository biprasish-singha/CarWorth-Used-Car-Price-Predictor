from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib

# Load saved files
model = joblib.load("car_price_predictor.pkl")
metadata = joblib.load("car_price_metadata.pkl")
vehicle_specs = joblib.load("vehicle_specifications.pkl")

# Create FastAPI application
app = FastAPI(title="Car Price Predictor", description="Machine Learning API for predicting used car prices", version="1.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Define the user input
class CarDetails(BaseModel):
    brand: str
    model: str
    variant: str
    make_year: int
    km_driven: float
    previous_owners: int
    transmission: str
    fuel_type: str

# Get available brands
@app.get("/brands")
def get_brands():
    brands = sorted(vehicle_specs["brand"].unique().tolist())
    return {"brands": brands}

# Get models available for selected brand
@app.get("/models/{brand}")
def get_models(brand: str):
    models = vehicle_specs[vehicle_specs["brand"] == brand]["model"].unique().tolist()
    return {"models": sorted(models)}

# Get variants available for selected brand
@app.get("/variants/{brand}")
def get_variants_by_brand(brand: str):
    variants = vehicle_specs[vehicle_specs["brand"] == brand]["variant"].unique().tolist()
    return {"variants": sorted(variants)}

# Find the best matching specification row
def find_specs(data: CarDetails):
    base = (vehicle_specs["brand"] == data.brand) & (vehicle_specs["model"] == data.model)
    variant = vehicle_specs["variant"] == data.variant
    fuel = vehicle_specs["fuel_type"] == data.fuel_type
    trans = vehicle_specs["transmission"] == data.transmission

    attempts = [
        ("exact", base & variant & fuel & trans),
        ("same_variant_and_fuel", base & variant & fuel),
        ("same_variant_and_transmission", base & variant & trans),
        ("same_variant", base & variant),
        ("same_model", base)]
    
    for match_level, mask in attempts:
        rows = vehicle_specs[mask]
        if not rows.empty:
            return rows.iloc[0], match_level
    return None, None

# Predict car price
@app.post("/predict")
def predict(data: CarDetails):

    # Get specifications for the closest matching vehicle
    car, match_level = find_specs(data)

    # Build model input to match the data frame used to train the model
    input_data = {"brand": data.brand.strip().upper(), "model": data.model.strip().upper(), "variant": data.variant.strip().upper(), 
                  "make_year": data.make_year, "km_driven": data.km_driven, "previous_owners": data.previous_owners, 
                  "transmission": data.transmission.strip().upper(),
                  "fuel_type": data.fuel_type.strip().upper(), "body_type": car["body_type"], "gear_box": car["gear_box"],
                  "drive_type": car["drive_type"], "steering_type": car["steering_type"], "rear_brake_type": car["rear_brake_type"],
                  "length": car["length"], "width": car["width"], "wheel_base": car["wheel_base"], "kerb_weight": car["kerb_weight"],
                  "max_power_delivered": car["max_power_delivered"], "max_torque_delivered": car["max_torque_delivered"],
                  "engine_capacity_cc": car["engine_capacity_cc"]}

    # Convert input into DataFrame
    input_df = pd.DataFrame([input_data])

    # Arrange columns in the same order as used for model training
    input_df = input_df[metadata["feature_columns"]]

    # Predict price
    prediction = float(model.predict(input_df)[0])

    # Return prediction (spec_match tells how closely the specs matched the selection)
    return {"predicted_price": round(prediction, 2), "spec_match": match_level}
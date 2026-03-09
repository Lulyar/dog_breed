import tensorflow as tf
import h5py
import json
import os

MODEL_PATH = 'model_anjing_10_kelas.keras'

try:
    print("Attempting to load weights directly, bypassing standard load_model...")
    # This is often caused by saving a model with incompatible TF versions 
    # Or functional API models saved as sequential.
    
    # We will try to inspect the model's structure via h5py since a .keras is a zip file
    import zipfile
    
    with zipfile.ZipFile(MODEL_PATH, 'r') as zip_ref:
        zip_ref.extractall("temp_model_extract")
        
    print("Extracted .keras file contents.")
    
    # Read config.json
    with open("temp_model_extract/config.json", "r") as f:
        config = json.load(f)
        
    print("Model Class Name:", config.get("class_name"))
    
    # This might tell us if we can construct the model manually
    
except Exception as e:
    import traceback
    traceback.print_exc()

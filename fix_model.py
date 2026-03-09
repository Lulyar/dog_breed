import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, InputLayer
from tensorflow.keras.applications import MobileNetV2
import h5py
import numpy as np
import zipfile

MODEL_PATH = 'model_anjing_10_kelas.keras'
EXTRACT_DIR = "temp_model_extract"

print("Building model manually...")
try:
    # Most Transfer Learning models are:
    # MobileNetV2 (headless) -> GlobalAveragePooling2D -> Dense(NumClasses)
    
    # We saw in the config that:
    # 1. Input shape is likely [None, 224, 224, 3] or [None, 150, 150, 3] (let's assume 224 for MobileNet default)
    # 2. Base model is probably MobileNetV2
    # 3. Dense layer has 10 units (softmax)
    
    # Let's inspect the weights file to confirm layers if possible
    # In .keras, there is usually model.weights.h5
    if zipfile.is_zipfile(MODEL_PATH):
        with zipfile.ZipFile(MODEL_PATH, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_DIR)
            
    # Load base model structure
    base_model = MobileNetV2(weights=None, include_top=False, input_shape=(224, 224, 3))
    
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dense(10, activation='softmax', name='dense_2')
    ])
    
    print("Model constructed.")
    
    # Let's try to load weights by name. This traverses the HDF5 structure.
    # In Keras 3, model.load_weights() can be smart enough
    try:
        model.load_weights(f"{EXTRACT_DIR}/model.weights.h5")
        print("Weights loaded successfully!")
        
        # Look good! Let's save it back as a clean file
        CLEAN_PATH = 'model_anjing_10_kelas_clean.keras'
        model.save(CLEAN_PATH)
        print(f"Clean model saved to {CLEAN_PATH}")
    except Exception as e_weights:
        print("Failed to load weights directly by name:", e_weights)
        import traceback
        traceback.print_exc()
        
except Exception as e:
    import traceback
    traceback.print_exc()

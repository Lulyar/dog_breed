import tensorflow as tf
import json
import os
import zipfile
import h5py
import numpy as np

MODEL_PATH = 'model_anjing_10_kelas.keras'
EXTRACT_DIR = "temp_model_extract"

try:
    print("Reconstructing model and loading weights...")
    
    # 1. Read the config
    with open(os.path.join(EXTRACT_DIR, "config.json"), "r") as f:
        config = json.load(f)
        
    print(f"Model Name: {config.get('name')}")
    
    # It seems to be a MobileNetV2 based model
    # We can try to load the model from the config directly using a lower-level API 
    # that might bypass the Strict input checking that fails in keras 3
    
    from keras.models import model_from_json
    
    # Keras 3 often fails loading Keras 2 Functional/Sequential mixed models. 
    # Let's try to parse it with the legacy deserializer if possible, or just build a fresh MobileNetV2 
    # and load weights by name.
    
    # Looking at the error: Layer "dense_2" expects 1 input(s), but it received 2 input tensors.
    # This usually happens when a layer was called with multiple inputs incorrectly during saving, or 
    # an older Keras version allowed it but the new one doesn't.
    
    # Let's try to create a standard model with the same architecture and load weights
    # We need to know the exact architecture. Best way is to look at the config.json.
    
    layers = config.get("config", {}).get("layers", [])
    print(f"Found {len(layers)} layers in config")
    
    # The safest way is to use safe_mode=False if allowed, but load_model(..., safe_mode=False) 
    # is often not enough. Let's try to build the model from config.
    
    # Modify the config to fix the problematic layer if we can spot it.
    # The error was about dense_2 receiving 2 inputs. Let's look at dense_2 in config.
    for layer in layers:
        if layer.get("config", {}).get("name") == "dense_2" or layer.get("name") == "dense_2":
            print("Found dense_2 layer in config!")
            # In sequential config, inbound_nodes might be the issue if it's there
            print(layer)
            
    # Let's try to just load the architecture from JSON and see if it fails the same way
    model_json = json.dumps(config)
    try:
        model = model_from_json(model_json)
        print("Model generated from json successfully!")
    except Exception as e:
        print("Failed to generate model from json:", e)
        
        # If it fails, we'll try to forcefully remove the bad inbound nodes if it's a functional model disguised as sequential
        if "config" in config and "layers" in config["config"]:
            for l in config["config"]["layers"]:
                if "inbound_nodes" in l:
                    # Sequential models shouldn't have complex inbound_nodes usually, or if they do, 
                    # they shouldn't have 2 inputs for a Dense layer unless it's a specific merged layer.
                    # Since dense_2 expects 1 input, we force it to 1.
                    if l.get("config", {}).get("name") == "dense_2" or l.get("name") == "dense_2":
                        if len(l["inbound_nodes"]) > 0 and len(l["inbound_nodes"][0]) > 1:
                            print("Fixing inbound nodes for dense_2")
                            l["inbound_nodes"] = [[l["inbound_nodes"][0][0]]] # Keep only first input
                            
            # Try again
            try:
                model_json_fixed = json.dumps(config)
                model = model_from_json(model_json_fixed)
                print("Model generated from FIXED json successfully!")
            except Exception as e2:
                 print("Failed again:", e2)

    
except Exception as e:
    import traceback
    traceback.print_exc()

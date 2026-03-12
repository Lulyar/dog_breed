import os
import io
import numpy as np
import traceback
from flask import Flask, request, jsonify, render_template
from PIL import Image

app = Flask(__name__)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# --- Model Configuration ---
WEIGHTS_PATH = 'model.weights.h5'
TARGET_SIZE = (224, 224)  # EfficientNetV2-B0 default input size
NUM_CLASSES = 10

print("=" * 50)
print("Loading EfficientNetV2-B0 model...")
print("=" * 50)

model = None

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.applications import EfficientNetV2B0


def try_load_model():
    """Try multiple strategies to load the model."""

    # ------------------------------------------------------------------
    # Strategy 1: EfficientNetV2B0 with include_top=True, classes=10
    # ------------------------------------------------------------------
    try:
        print("[Strategy 1] EfficientNetV2B0(include_top=True, classes=10)...")
        m = EfficientNetV2B0(
            weights=None,
            include_top=True,
            classes=NUM_CLASSES,
            classifier_activation='softmax',
            input_shape=(224, 224, 3)
        )
        m.load_weights(WEIGHTS_PATH)
        print("[Strategy 1] SUCCESS!")
        return m
    except Exception as e:
        print(f"[Strategy 1] Failed: {e}")

    # ------------------------------------------------------------------
    # Strategy 2: Sequential(EfficientNetV2B0(include_top=False) + head)
    # ------------------------------------------------------------------
    try:
        print("[Strategy 2] Sequential + include_top=False + custom head...")
        base = EfficientNetV2B0(
            weights=None,
            include_top=False,
            input_shape=(224, 224, 3)
        )
        m = Sequential([
            base,
            GlobalAveragePooling2D(),
            Dense(NUM_CLASSES, activation='softmax')
        ])
        m.load_weights(WEIGHTS_PATH)
        print("[Strategy 2] SUCCESS!")
        return m
    except Exception as e:
        print(f"[Strategy 2] Failed: {e}")

    # ------------------------------------------------------------------
    # Strategy 3: Load weights by name (skip mismatched layers)
    # ------------------------------------------------------------------
    try:
        print("[Strategy 3] Sequential + load_weights(by_name=True, skip)...")
        base = EfficientNetV2B0(
            weights=None,
            include_top=False,
            input_shape=(224, 224, 3)
        )
        m = Sequential([
            base,
            GlobalAveragePooling2D(),
            Dense(NUM_CLASSES, activation='softmax')
        ])
        m.load_weights(WEIGHTS_PATH, skip_mismatch=True, by_name=True)
        print("[Strategy 3] SUCCESS (some weights may be skipped)!")
        return m
    except Exception as e:
        print(f"[Strategy 3] Failed: {e}")

    # ------------------------------------------------------------------
    # Strategy 4: Re-zip as .keras and use load_model
    # ------------------------------------------------------------------
    try:
        import zipfile
        keras_path = 'model_efnv2b0.keras'
        print(f"[Strategy 4] Re-packaging as {keras_path} and using load_model...")
        with zipfile.ZipFile(keras_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write('config.json', 'config.json')
            zf.write(WEIGHTS_PATH, 'model.weights.h5')
            if os.path.exists('metadata.json'):
                zf.write('metadata.json', 'metadata.json')
        from tensorflow.keras.models import load_model
        m = load_model(keras_path, compile=False)
        print("[Strategy 4] SUCCESS!")
        return m
    except Exception as e:
        print(f"[Strategy 4] Failed: {e}")

    return None


model = try_load_model()
if model is not None:
    print("=" * 50)
    print("Model loaded successfully!")
    print(f"  Input shape  : {model.input_shape}")
    print(f"  Output shape : {model.output_shape}")
    print(f"  Total params : {model.count_params():,}")
    print("=" * 50)

    # Warmup: run a dummy prediction so TensorFlow compiles the graph now
    # instead of making the first real prediction slow
    print("Warming up model (first prediction compile)...")
    dummy = np.zeros((1, 224, 224, 3), dtype=np.float32)
    _ = model(dummy, training=False)
    print("Warmup done! Model is ready for fast predictions.")
else:
    print("=" * 50)
    print("FAILED: Could not load model with any strategy!")
    print("=" * 50)

# Class Names mapped directly from the alphabetical folder names
CLASS_NAMES = [
    "Chihuahua",
    "Japanese Spaniel",
    "Maltese Dog",
    "Pekinese",
    "Shih-Tzu",
    "Blenheim Spaniel",
    "Papillon",
    "Toy Terrier",
    "Rhodesian Ridgeback",
    "Afghan Hound"
]


def preprocess_image(img: Image.Image, target_size=TARGET_SIZE):
    """Preprocess PIL Image in memory for prediction.

    EfficientNetV2-B0 has built-in Rescaling + Normalization,
    so just pass raw pixel values (0-255), no manual normalization.
    """
    img = img.convert('RGB')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32)  # (H, W, 3) values [0, 255]
    img_array = np.expand_dims(img_array, axis=0)  # (1, H, W, 3)
    return img_array


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded on server.'}), 500

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        # Read image directly in memory (no saving to disk)
        img_bytes = file.read()
        img = Image.open(io.BytesIO(img_bytes))

        # Preprocess image in memory
        img_tensor = preprocess_image(img, target_size=TARGET_SIZE)

        # Direct model call (MUCH faster than model.predict() for single images)
        predictions = model(img_tensor, training=False).numpy()
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx]) * 100
        predicted_class = CLASS_NAMES[class_idx]

        return jsonify({
            'class': predicted_class,
            'confidence': f"{confidence:.2f}%"
        })
    except Exception as e:
        return jsonify({
            'error': 'Prediction failed: ' + str(e)
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)


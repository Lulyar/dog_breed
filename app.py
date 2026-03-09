import os
import numpy as np
import traceback
from flask import Flask, request, jsonify, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# Load Model
MODEL_PATH = 'model_anjing_10_kelas_clean.keras'
print(f"Loading model from {MODEL_PATH}...")
try:
    model = load_model(MODEL_PATH)
    # Default input shape: (None, height, width, channels)
    # If the model has an input shape, we try to use it
    input_shape = model.input_shape
    if input_shape and len(input_shape) >= 3:
        TARGET_SIZE = (input_shape[1], input_shape[2])
        print(f"Model loaded successfully. Inferred target size: {TARGET_SIZE}")
    else:
        TARGET_SIZE = (224, 224) 
        print(f"Model loaded successfully. Could not infer target size, defaulting to: {TARGET_SIZE}")
except Exception as e:
    print(f"Error loading model: {e}")
    TARGET_SIZE = (224, 224)
    model = None

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

def preprocess_image(img_path, target_size=TARGET_SIZE):
    img = image.load_img(img_path, target_size=target_size)
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array /= 255.0  # Normalize to [0,1]
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

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Preprocess image
            img_tensor = preprocess_image(filepath, target_size=TARGET_SIZE)
            
            # Predict
            predictions = model.predict(img_tensor)
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx]) * 100
            predicted_class = CLASS_NAMES[class_idx]

            # Cleanup
            if os.path.exists(filepath):
                os.remove(filepath)

            return jsonify({
                'class': predicted_class,
                'confidence': f"{confidence:.2f}%"
            })
        except ValueError as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Value error (check target size): {str(e)}'}), 500
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Prediction failed: ' + str(e) + '\n' + traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

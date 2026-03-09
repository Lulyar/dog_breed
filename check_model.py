import tensorflow as tf
import traceback

print("TensorFlow Version:", tf.__version__)
try:
    print("Attempting to load model...")
    model = tf.keras.models.load_model('model_anjing_10_kelas.keras', compile=False)
    print("Model loaded successfully!")
    model.summary()
except Exception as e:
    print("Failed to load model.")
    traceback.print_exc()

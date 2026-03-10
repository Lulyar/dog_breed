# Dog Breed Classification Web Application

A web application designed to identify and classify 10 different dog breeds from uploaded images. The application is built using Python, Flask for the backend, and TensorFlow/Keras for the machine learning model.

## Algorithm and Architecture

- Algorithm: Deep Learning - Convolutional Neural Network (CNN)
- Architecture: MobileNetV2

The model utilizes MobileNetV2, which provides a lightweight and efficient architecture suitable for web-based image classification tasks while maintaining good accuracy.

## Supported Dog Breeds

The model is trained to recognize the following 10 dog breeds:
1. Chihuahua
2. Japanese Spaniel
3. Maltese Dog
4. Pekinese
5. Shih-Tzu
6. Blenheim Spaniel
7. Papillon
8. Toy Terrier
9. Rhodesian Ridgeback
10. Afghan Hound

## Requirements

Ensure you have Python installed. The following libraries are required to run the application:
- Flask
- TensorFlow
- NumPy
- Werkzeug

You can install them using pip :
pip install Flask tensorflow numpy Werkzeug

## How to Run the Application

1. Open a terminal or command prompt in the project directory.
2. Make sure you have the required dependencies installed.
3. Run the Flask application by executing the following command:
   python app.py
4. The server will start running on port 5000.
5. Open your web browser and navigate to:
   http://127.0.0.1:5000 or http://localhost:5000

## Project Structure

- app.py : The main Flask application script that handles routing and model prediction.
- model_anjing_10_kelas_clean.keras : The refined and cleaned MobileNetV2 trained model.
- static/ : Directory containing static assets such as CSS styles and JavaScript files.
- templates/ : Directory containing the HTML templates, specifically index.html for the user interface.
- uploads/ : Directory used to temporarily store images uploaded by the user before they are processed by the model.
- .gitignore : Specifies intentionally untracked files to ignore for Git.

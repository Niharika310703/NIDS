from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)

# Load Model and Preprocessing Tools
try:
    model = load_model('nids_transformer.keras')  # Ensure correct file path
    scaler = joblib.load("scaler.pkl")  # Ensure this file exists
except Exception as e:
    print(f"Error loading model or preprocessing tools: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict_page', methods=['GET'])
def predict_page():
    return render_template('predict.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Extract features from form
        data = [float(request.form[f'feature{i+1}']) for i in range(48)]
        data = np.array(data).reshape(1, -1)

        # Apply scaling
        data = scaler.transform(data)

        # Reshape correctly for the Transformer model (batch_size, time_step, features)
        data = data.reshape(1, 1, 48)

        # Make prediction
        prediction = model.predict(data)

        # Attack Class Labels
        attack_classes = ['Benign', 'Fuzzers', 'Exploits', 'Backdoor', 'Generic',
                          'DoS', 'Reconnaissance', 'Shellcode', 'Analysis', 'Worms']
        predicted_class = attack_classes[np.argmax(prediction)]

        # Prepare JSON response
        if predicted_class == "Benign":
            return jsonify({'result': "Benign"})  # Match JS check
        else:
            return jsonify({'result': f"Intrusion Detected: {predicted_class}"})  # Attack detected

    except Exception as e:
        return jsonify({'error': str(e)})  # Send error as JSON

if __name__ == '__main__':
    app.run(debug=True)

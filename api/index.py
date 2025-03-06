from flask import Flask, request, jsonify
from deepface import DeepFace
import os
import tempfile
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

@app.route('/api/compare', methods=['POST'])
def compare_faces():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Both image1 and image2 files are required'}), 400
    
    # Get the files from request
    image1 = request.files['image1']
    image2 = request.files['image2']
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate unique filenames
        filename1 = f"{uuid.uuid4()}_{secure_filename(image1.filename)}"
        filename2 = f"{uuid.uuid4()}_{secure_filename(image2.filename)}"
        
        # Save files temporarily
        filepath1 = os.path.join(temp_dir, filename1)
        filepath2 = os.path.join(temp_dir, filename2)
        
        image1.save(filepath1)
        image2.save(filepath2)
        
        try:
            # Verify faces using DeepFace
            result = DeepFace.verify(
                img1_path=filepath1,
                img2_path=filepath2
            )
            
            # Return the verification result
            return jsonify({
                'verified': result['verified'],
                'distance': result['distance'],
                'threshold': result['threshold'],
                'model': result['model']
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return '''
    <html>
        <body>
            <h1>Face Comparison API</h1>
            <p>Send a POST request to /api/compare with two images to compare faces.</p>
        </body>
    </html>
    '''

# Vercel serverless handler
@app.route('/<path:path>')
def catch_all(path):
    return home()
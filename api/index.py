from flask import Flask, request, jsonify
from deepface import DeepFace
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Definir o diretório para salvar as imagens temporárias
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Rota para comparar as imagens
@app.route('/compare', methods=['POST'])
def compare_images():
    if 'image1' not in request.files or 'image2' not in request.files:
        return jsonify({'error': 'Both images are required'}), 400

    image1 = request.files['image1']
    image2 = request.files['image2']

    if image1.filename == '' or image2.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(image1.filename) or not allowed_file(image2.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    # Salvar as imagens temporariamente
    image1_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image1.filename))
    image2_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image2.filename))

    image1.save(image1_path)
    image2.save(image2_path)

    # Usar o DeepFace para comparar as imagens
    try:
        result = DeepFace.verify(image1_path, image2_path)
        # Obter o nível de match
        match = result["verified"]

        # Limpar as imagens após a comparação
        os.remove(image1_path)
        os.remove(image2_path)

        return jsonify({'match': match, 'similarity': result['distance']}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Certifique-se de que o diretório de uploads exista
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(debug=True)

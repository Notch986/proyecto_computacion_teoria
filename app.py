import os
from flask import Flask, request, render_template
import cv2
import ollama
import time

# Inicialización de Flask
app = Flask(__name__)

# Carpeta para almacenar imágenes
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Función para segmentar imágenes con OpenCV
def segment_image(image_path):
    # Cargar imagen
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Usar un umbral para segmentar la imagen
    _, segmented = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # Guardar la imagen segmentada
    segmented_path = os.path.join(UPLOAD_FOLDER, 'segmented_' + os.path.basename(image_path))
    cv2.imwrite(segmented_path, segmented)
    return segmented_path

# Función para interactuar con LLaVA
def analyze_webpage(image_path, evaluation_type):
    start_time = time.time()

    # Configuración del mensaje según el tipo de evaluación
    if evaluation_type == 'aesthetic':
        content = 'Evaluate the design of the webpage. Pay attention to typography, colors, layout, and image placement. What changes would you suggest for better visual appeal?'
    elif evaluation_type == 'ux':
        content = 'Assess the user experience of this webpage. Is the navigation intuitive? Are there any recommendations for improving accessibility and overall ease of use?'
    else:
        content = 'Please evaluate the webpage and provide suggestions for improvement.'

    # Llamada a LLaVA
    response = ollama.chat(
        model='llava:7b',
        messages=[{
            'role': 'user',
            'content': content,
            'images': [image_path]
        }]
    )

    end_time = time.time()
    print(f"Request processed in {(end_time - start_time) / 60} minutes")

    return response['message']['content']

# Rutas de la aplicación
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Obtener la imagen subida y guardar en la carpeta de uploads
        file = request.files['image']
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Obtener el tipo de evaluación
        evaluation_type = request.form['evaluation_type']

        # Segmentar la imagen
        segmented_image_path = segment_image(file_path)

        # Analizar la imagen con LLaVA
        response = analyze_webpage(segmented_image_path, evaluation_type)

        # Retornar la página de resultados con la respuesta de LLaVA
        return render_template('result.html', result=response, image_path=segmented_image_path)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

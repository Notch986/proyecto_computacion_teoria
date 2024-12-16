import os
import cv2
import numpy as np
from flask import Flask, request, render_template
import ollama
import time

# Inicialización de Flask
app = Flask(__name__)

# Carpeta para almacenar imágenes
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegúrate de que el directorio 'uploads' existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Función para segmentar imágenes con OpenCV
def segment_image(image_path):
    # Cargar imagen
    image = cv2.imread(image_path)
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar un desenfoque gaussiano para reducir el ruido
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Usar el detector de bordes de Canny para encontrar contornos
    edges = cv2.Canny(blurred, 50, 150)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Crear una imagen en blanco para dibujar los contornos
    segmented_image = np.zeros_like(image)
    
    # Dibujar los contornos encontrados sobre la imagen segmentada
    cv2.drawContours(segmented_image, contours, -1, (0, 255, 0), 3)
    
    # Guardar la imagen segmentada
    segmented_path = os.path.join(UPLOAD_FOLDER, 'segmented_' + os.path.basename(image_path))
    cv2.imwrite(segmented_path, segmented_image)
    
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
        
        if file:
            # Guardar el archivo en el directorio de uploads
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)

            # Obtener el tipo de evaluación
            evaluation_type = request.form['evaluation_type']

            # Segmentar la imagen
            segmented_image_path = segment_image(file_path)

            # Analizar la imagen con LLaVA
            response = analyze_webpage(segmented_image_path, evaluation_type)

            # Retornar la página de resultados con la respuesta de LLaVA
            return render_template('result.html', 
                                   result=response, 
                                   image_path='uploads/' + file.filename, 
                                   segmented_image_path='uploads/segmented_' + file.filename)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)

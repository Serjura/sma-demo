import os
import requests
from waitress import serve
import base64
from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

API_URL = os.getenv("API_URL", "http://localhost:5000/model/predict")

def draw_line(draw, line):
    draw.line(line, fill=(255, 0, 0), width=2)

def draw_point(draw, point):
    radius = 5
    x, y = point
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(0, 255, 0))

def predict_pose(image_data):
    try:
        files = {'file': ('image.jpg', image_data)}
        response = requests.post(API_URL, files=files)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException as e:
        return None

def mark_predictions_on_image(image_data, predictions):
    img = Image.open(BytesIO(image_data))
    draw = ImageDraw.Draw(img)
    for prediction in predictions.get('predictions', []):
        for line in prediction.get('pose_lines', []):
            draw_line(draw, line['line'])
        for body_part in prediction.get('body_parts', []):
            draw_point(draw, (body_part['x'], body_part['y']))
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return buffered.getvalue()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        image = request.files['image']
        if image:
            image_data = image.read()
            response = predict_pose(image_data)
            if response is not None:
                marked_image = mark_predictions_on_image(image_data, response)
                return jsonify(
                    marked_image=base64.b64encode(marked_image).decode('utf-8'),
                )
    return render_template('index.html')


if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8080)

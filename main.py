import requests
import logging
import base64
from flask import Flask, render_template, request, jsonify
from PIL import Image, ImageDraw
from io import BytesIO

app = Flask(__name__)

API_URL = "http://localhost:5000/model/predict"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
        logger.error("An error occurred during API request: %s", e)
        return None
def extract_detected_parts(response):
    detected_parts = []
    for prediction in response.get('predictions', []):
        for body_part in prediction.get('body_parts', []):
            part_name = body_part.get('part_name', 'Unknown')
            detected_parts.append(part_name)
    return detected_parts

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
                log_messages = response.get('log_messages', [])
                marked_image = mark_predictions_on_image(image_data, response)
                detected_parts = extract_detected_parts(response)
                return jsonify(
                    log_messages=log_messages,
                    marked_image=base64.b64encode(marked_image).decode('utf-8'),
                    detected_parts=detected_parts
                )
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=8080)

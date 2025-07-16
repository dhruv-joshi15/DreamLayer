from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from dream_layer_backend_utils.fetch_advanced_models import get_controlnet_models

# Setup Flask app and CORS
app = Flask(__name__)
CORS(app)

# Set output directory
COMFY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(COMFY_ROOT, "Dream_Layer_Resources", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"Using output directory: {OUTPUT_DIR}")

# =========================
# PATCH: Return checkpoints from ComfyUI/models/checkpoints
# =========================
@app.route('/api/models', methods=['GET'])
def get_models():
    try:
        checkpoint_dir = os.path.join(COMFY_ROOT, "ComfyUI", "models", "checkpoints")
        if not os.path.exists(checkpoint_dir):
            return jsonify({"status": "success", "models": []})

        models = []
        for filename in os.listdir(checkpoint_dir):
            if filename.endswith(('.safetensors', '.ckpt')):
                models.append({
                    "id": filename,
                    "name": os.path.splitext(filename)[0],
                    "filename": filename
                })

        return jsonify({"status": "success", "models": models})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================
# ControlNet models
# =========================
@app.route('/api/controlnet/models', methods=['GET'])
def get_controlnet():
    try:
        controlnet_models = get_controlnet_models()
        return jsonify({"status": "success", "models": controlnet_models})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================
# Serve Generated Images
# =========================
@app.route('/api/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

# =========================
# Dummy Txt2Img POST handler
# =========================
@app.route('/api/txt2img', methods=['POST'])
def handle_txt2img():
    return jsonify({
        "status": "success",
        "message": "This is a stub for txt2img endpoint."
    })

# =========================
# Upload ControlNet images (stub)
# =========================
@app.route('/api/upload-controlnet-image', methods=['POST'])
def upload_controlnet_image():
    return jsonify({"status": "success", "message": "Image received (not processed)."})

# =========================
# Run the Flask App
# =========================
if __name__ == '__main__':
    print("Starting Text2Image Handler Server...")
    print("Listening at http://localhost:5001/api/txt2img")
    print("ControlNet endpoints:")
    print("- GET /api/controlnet/models")
    print("- POST /api/upload-controlnet-image")
    print("- GET /api/images/<filename>")
    app.run(debug=True, port=5001)

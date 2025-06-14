from flask import Flask, render_template, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

def extraer_video_id(youtube_url):
    """
    Extrae el ID del video desde URLs como:
    https://www.youtube.com/watch?v=KYs3M_qB6hs
    https://youtu.be/KYs3M_qB6hs
    """
    patrones = [
        r"v=([a-zA-Z0-9_-]{11})",       # youtube.com/watch?v=...
        r"youtu\.be/([a-zA-Z0-9_-]{11})"  # youtu.be/...
    ]
    for patron in patrones:
        coincidencia = re.search(patron, youtube_url)
        if coincidencia:
            return coincidencia.group(1)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcripcion', methods=['GET'])
def obtener_transcripcion():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Falta el parámetro 'url'"}), 400

    video_id = extraer_video_id(url)
    if not video_id:
        return jsonify({"error": "No se pudo extraer el ID del video de la URL proporcionada."}), 400

    try:
        fetched_transcript = YouTubeTranscriptApi.get_transcript(video_id)
        texto_completo = " ".join(snippet['text'] for snippet in fetched_transcript)
        return jsonify({"video_id": video_id, "transcripcion": texto_completo})
    except TranscriptsDisabled:
        return jsonify({"error": "La transcripción está deshabilitada para este video."}), 403
    except NoTranscriptFound:
        return jsonify({"error": "No se encontró transcripción para este video."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
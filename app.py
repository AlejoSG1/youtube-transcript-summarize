from flask import Flask, render_template, jsonify, request
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re

app = Flask(__name__)

# Configuración del proxy residencial
proxy_config = GenericProxyConfig(
    http_url="http://brd-customer-hl_f7c60629-zone-residential_proxy1-country-us:mnx456wtp34s@brd.superproxy.io:33335",
    https_url="https://brd-customer-hl_f7c60629-zone-residential_proxy1-country-us:mnx456wtp34s@brd.superproxy.io:33335",
)

# Instancia personalizada del API con proxy
ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

def extraer_video_id(youtube_url):
    patrones = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})"
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
        fetched_transcript = ytt_api.get_transcript(video_id)
        texto_completo = " ".join(snippet['text'] for snippet in fetched_transcript)
        return jsonify({"video_id": video_id, "transcripcion": texto_completo})
    except TranscriptsDisabled:
        return jsonify({"error": "La transcripción está deshabilitada para este video."}), 403
    except NoTranscriptFound:
        return jsonify({"error": "No se encontró transcripción para este video."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
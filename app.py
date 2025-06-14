from flask import Flask, render_template, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Esta línea carga tu HTML

@app.route('/transcripcion/<video_id>', methods=['GET'])
def obtener_transcripcion(video_id):
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

if __name__ == '__main__':
    app.run(debug=True)

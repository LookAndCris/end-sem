from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import time
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Configuración de API y rutas
API_KEY = os.getenv("SEMRUSH_API_KEY")  # Asegúrate de definir esta variable en un archivo .env
SEMRUSH_ENDPOINT = "https://api.semrush.com/"

@app.route('/fetch-keywords', methods=['POST'])
def fetch_keywords():
    """
    Ruta para obtener datos de palabras clave desde la API de Semrush
    """
    data = request.get_json()
    databases = data.get("databases", [])
    keywords = data.get("keywords", [])

    if not databases or not keywords:
        return jsonify({"error": "Se requieren 'databases' y 'keywords'"}), 400

    results = {}
    for database in databases:
        results[database] = []
        for keyword in keywords:
            params = {
                "type": "phrase_this",
                "key": API_KEY,
                "phrase": keyword,
                "database": database,
                "export_columns": "Ph,Nq,Cp,Co,Nr,Kd",
            }
            try:
                # Realizar la solicitud a Semrush
                response = requests.get(SEMRUSH_ENDPOINT, params=params)
                response.raise_for_status()
                results[database].append({
                    "keyword": keyword,
                    "data": response.text
                })
                # Pausar entre solicitudes para evitar superar los límites de la API
                time.sleep(1.0)
            except requests.exceptions.RequestException as e:
                results[database].append({
                    "keyword": keyword,
                    "data": None,
                    "error": str(e)
                })
    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

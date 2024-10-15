from flask import jsonify
from app import app

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "OK"}), 200

from flask import jsonify
from app import py_app


@py_app.route('/healthcheck', methods = ['GET'])
def healthcheck():
    return jsonify({'status': 'OK'}), 200
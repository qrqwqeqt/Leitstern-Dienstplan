from flask import jsonify
from app import app
import time



@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    current_time = time.ctime()
    return jsonify({"status": "OK",
                    "time": current_time
                    }), 200


from flask import Flask, request, jsonify
import json
from trim_video import lambda_handler


app = Flask(__name__)


@app.route("/", methods=["GET"])
def gethello():
    return jsonify(
        {
            "message": "Hello world!",
        }
    )


@app.route("/trim", methods=["POST"])
def trim_video():
    try:
        body = json.loads(request.data)
        return lambda_handler({"body": body}, {})


    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, request, jsonify
from trim_video import lambda_handler

app = Flask(__name__)

@app.route("/trim", methods=["POST"])
def trim_video():
    body = request.get_json(force=True)
    return lambda_handler({"body": body},{})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

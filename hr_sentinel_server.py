# hr_sentinel_server.py
from flask import Flask, jsonify, request

db = []

app = Flask(__name__)


@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    """
    Receive the posting JSON
    Verify the JSON contains correct keys and data
    If data is bad, reject request with bad status to client
    If data is good, add patient to database
    return good status to client
    """
    in_dict = request.get_json()
    add_patient_to_db(in_dict["patient_id"], in_dict["attending_email"],
                      in_dict["patient_age"])
    return "Patient added", 200


if __name__ == "__main__":
    # init_database()
    app.run()

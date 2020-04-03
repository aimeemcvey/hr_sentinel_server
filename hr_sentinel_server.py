# hr_sentinel_server.py
from flask import Flask, jsonify, request

patient_db = []

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
    check_result = verify_new_patient_info(in_dict)
    add_patient_to_db(in_dict["patient_id"], in_dict["attending_email"],
                      in_dict["patient_age"])
    return "Patient added", 200


def add_patient_to_db(id, email, age):
    new_patient = {"patient_id": id, "attending_email": email,
                   "patient_age": age}
    patient_db.append(new_patient)
    print("db is {}" .format(patient_db))
    return True


def verify_new_patient_info(in_dict):
    expected_keys = ("patient_id", "attending_email", "patient_age")
    expected_types = (int, str, int)
    # must be able to parse inputs for numbers though
    for i, key in enumerate(expected_keys):
        if key not in in_dict.keys():
            return "{} key not found".format(key)
        if type(in_dict[key]) is not expected_types[i]:
            if key == "patient_id" or key == "patient_age":
                try:
                    int(in_dict[key])
                except ValueError:
                    return "{} value not correct type".format(key)
            else:
                return "{} value not correct type".format(key)
    return True


if __name__ == "__main__":
    # init_database()
    app.run()

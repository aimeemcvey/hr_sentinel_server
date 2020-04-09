# hr_sentinel_server.py
from flask import Flask, jsonify, request
import logging
from datetime import datetime
import requests

logging.basicConfig(filename="hr_sentinel_server_info.log", filemode="w",
                    level=logging.INFO)

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
    if check_result is not True:
        return check_result, 400
    add_patient_to_db(int(in_dict["patient_id"]), in_dict["attending_email"],
                      int(in_dict["patient_age"]))
    return "Patient added", 200


def add_patient_to_db(id, email, age):
    new_patient = {"patient_id": id, "attending_email": email,
                   "patient_age": age, "heart_rate": []}
    patient_db.append(new_patient)
    logging.info("New patient added to database: ID={}"
                 .format(new_patient["patient_id"]))
    print("db is {}".format(patient_db))
    return new_patient


def verify_new_patient_info(in_dict):
    expected_keys = ("patient_id", "attending_email", "patient_age")
    expected_types = (int, str, int)
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


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    """
    Receive the posting JSON
    Verify the JSON contains correct keys and data
    If data is bad, reject request with bad status to client
    If data is good, add HR to database, send email
    return good status to client
    """
    in_dict = request.get_json()
    check_result = verify_heart_rate_info(in_dict)
    if check_result is not True:
        return check_result, 400
    if is_patient_in_database(in_dict["patient_id"]) is False:
        return "Patient {} is not found on server" \
                   .format(in_dict["patient_id"]), 400
    add_hr_to_db(in_dict)
    tach = is_tachycardic(in_dict)
    add_tach_to_db(in_dict, tach)
    if tach:
        email_physician(in_dict)
    if add_tach_to_db:
        return "Heart rate added to patient ID {}" \
                   .format(in_dict["patient_id"]), 200
    # else:
    #     return "Unknown problem", 400


def verify_heart_rate_info(in_dict):
    expected_keys = ("patient_id", "heart_rate")
    expected_types = (int, int)
    for i, key in enumerate(expected_keys):
        if key not in in_dict.keys():
            return "{} key not found".format(key)
        if type(in_dict[key]) is not expected_types[i]:
            # if key == "patient_id" or key == "heart_rate":
            try:
                in_dict[key] = int(in_dict[key])
            except ValueError:
                return "{} value not correct type".format(key)
            # else:
            #     return "{} value not correct type".format(key)
    return True


def is_patient_in_database(id):
    for patient in patient_db:
        if patient["patient_id"] == id:
            return True
    return False


def add_hr_to_db(in_dict):
    for patient in patient_db:
        if patient["patient_id"] == in_dict["patient_id"]:
            patient["latest_hr"] = in_dict["heart_rate"]
            return True
    return False


def is_tachycardic(in_dict):
    print("in_dict is {}" .format(in_dict))
    for patient in patient_db:
        if patient["patient_id"] == in_dict["patient_id"]:
            hr = patient["latest_hr"]
            if (1 <= patient["patient_age"] < 3 and hr > 151) \
                    or (3 <= patient["patient_age"] < 5 and hr > 137) \
                    or (5 <= patient["patient_age"] < 8 and hr > 133) \
                    or (8 <= patient["patient_age"] < 12 and hr > 130) \
                    or (12 <= patient["patient_age"] < 15 and hr > 119) \
                    or (patient["patient_age"] >= 15 and hr > 100):
                return True
            else:
                return False


def add_tach_to_db(in_dict, tach):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if tach:
        status = "tachycardic"
    elif not tach:
        status = "not tachycardic"
    for patient in patient_db:
        if patient["patient_id"] == in_dict["patient_id"]:
            patient["heart_rate"].append((in_dict["heart_rate"],
                                          status, timestamp))
            print("db is {}".format(patient_db))
            return True
    return False


def email_physician(in_dict):
    # if tachycardic, send email
    # patient_id, the tachycardic heart rate, and dt stamp
    for patient in patient_db:
        if patient["patient_id"] == in_dict["patient_id"]:
            to_email = patient["attending_email"]
            content = "Patient {} is tachycardic with HR of {} at {}" \
                      .format(patient["patient_id"], patient["heart_rate"][-1][0],
                              patient["heart_rate"][-1][2])
    subject = "Urgent Tachycardia Alert"
    from_email = "ajm111@duke.edu"
    email = {"from_email": from_email, "to_email": to_email, "subject": subject,
             "content": content}
    print(email)
    email_server = "http://vcm-7631.vm.duke.edu:5007/hrss/send_email"
    r = requests.post(email_server, json=email)
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    # init_database()
    app.run()

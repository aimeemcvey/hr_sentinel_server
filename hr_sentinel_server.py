# hr_sentinel_server.py
from flask import Flask, jsonify, request
import logging
from datetime import datetime
import requests
import statistics

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
        email = compose_email(in_dict)
        email_physician(email)
        logging.info("Tachycardic heart rate of {} detected from patient ID {} "
                     "with attending email {}"
                     .format(in_dict["heart_rate"], in_dict["patient_id"],
                             email["to_email"]))
    if add_tach_to_db:
        return "Heart rate added to patient ID {}" \
                   .format(in_dict["patient_id"]), 200
    else:
        return "Unknown problem", 400


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


def compose_email(in_dict):
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
    email = {"from_email": from_email, "to_email": to_email,
             "subject": subject, "content": content}
    return email


def email_physician(email):
    email_server = "http://vcm-7631.vm.duke.edu:5007/hrss/send_email"
    r = requests.post(email_server, json=email)
    if r.status_code != 200:
        print("Error: {} - {}".format(r.status_code, r.text))
    else:
        print("Success: {}".format(r.text))


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_latest_hr(patient_id):
    check_result = verify_id_input(patient_id)
    if type(check_result) is str:
        return check_result, 400
    answer = generate_latest_hr(check_result)
    if answer is False:
        return "Unknown Error", 400
    elif type(answer) is str:
        return answer, 400
    else:
        return answer, 200


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_all_hr(patient_id):
    check_result = verify_id_input(patient_id)
    if type(check_result) is str:
        return check_result, 400
    answer = generate_all_hr(check_result)
    if answer is False:
        return "Unknown Error", 400
    elif type(answer) is str:
        return answer, 400
    else:
        return jsonify(answer), 200


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def get_avg_hr(patient_id):
    check_result = verify_id_input(patient_id)
    if type(check_result) is str:
        return check_result, 400
    hr_list = generate_all_hr(check_result)
    if hr_list is False:
        return "Unknown Error", 400
    elif type(hr_list) is str:
        return hr_list, 400
    else:
        avg_hr = generate_avg_hr(hr_list)
        return jsonify(avg_hr), 200


def verify_id_input(patient_id):
    try:
        id = int(patient_id)
    except ValueError:
        return "Bad patient ID in URL"
    if is_patient_in_database(id) is False:
        return "Patient ID {} does not exist in database".format(id)
    return id


def generate_latest_hr(patient_id):
    for patient in patient_db:
        if patient["patient_id"] == patient_id:
            if len(patient["heart_rate"]) == 0:
                return "No heart rates in database"
            out_latest_hr = {"heart_rate": patient["heart_rate"][-1][0],
                             "status": patient["heart_rate"][-1][1],
                             "timestamp": patient["heart_rate"][-1][2]}
            return out_latest_hr
    return False


def generate_all_hr(patient_id):
    for patient in patient_db:
        if patient["patient_id"] == patient_id:
            if len(patient["heart_rate"]) == 0:
                return "No heart rates in database"
            all_hr = []
            for hr in patient["heart_rate"]:
                all_hr.append(hr[0])
            return all_hr
    return False


def generate_avg_hr(hr_list):
    avg_hr = round(statistics.mean(hr_list))
    return avg_hr


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def post_heart_rate_interval_avg():
    in_dict = request.get_json()
    check_result = verify_interval_info(in_dict)
    if check_result is not True:
        return check_result, 400
    if is_patient_in_database(in_dict["patient_id"]) is False:
        return "Patient {} is not found on server" \
                   .format(in_dict["patient_id"]), 400
    hr_list = generate_select_hr(in_dict["patient_id"],
                                 in_dict["heart_rate_average_since"])
    if hr_list is False:
        return "Unknown Error", 400
    elif type(hr_list) is str:
        return hr_list, 400
    else:
        avg_hr = generate_avg_hr(hr_list)
        return jsonify(avg_hr), 200


def verify_interval_info(in_dict):
    expected_keys = ("patient_id", "heart_rate_average_since")
    expected_types = (int, str)
    for i, key in enumerate(expected_keys):
        if key not in in_dict.keys():
            return "{} key not found".format(key)
        if type(in_dict[key]) is not expected_types[i]:
            if key == "patient_id":
                try:
                    in_dict[key] = int(in_dict[key])
                except ValueError:
                    return "{} value not correct type".format(key)
            else:
                return "{} value not correct type".format(key)
    return True


def generate_select_hr(patient_id, sent_time):
    for patient in patient_db:
        if patient["patient_id"] == patient_id:
            if len(patient["heart_rate"]) == 0:
                return "No heart rates in database"
            select_hr = []
            for hr in patient["heart_rate"]:
                if hr[2] >= sent_time:
                    select_hr.append(hr[0])
            if len(select_hr) == 0:
                return "No heart rates in database since {}".format(sent_time)
            else:
                return select_hr
    return False


if __name__ == "__main__":
    # init_database()
    app.run()

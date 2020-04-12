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
    """Adds new patient to the patient database via ID

    When a post request is made to /api/new_patient, the input
    must be validated before the patient ID, attending email,
    and patient age are added to the patient database.

    Args:
        None

    Returns:
        str: results of post request
        int: HTTP status code
    """
    in_dict = request.get_json()
    check_result = verify_new_patient_info(in_dict)
    if check_result is not True:
        return check_result, 400
    add_patient_to_db(int(in_dict["patient_id"]), in_dict["attending_email"],
                      int(in_dict["patient_age"]))
    return "Patient added", 200


def add_patient_to_db(id, email, age):
    """Adds new patient to patient database list via ID

    The patient ID, attending physician email, and patient age
    are added to the patient database to maintain proper records
    of monitored patient heart rates.

    Args:
        id (int): patient ID
        email (str): attending physician email
        age (int): patient age

    Returns:
        dict: new patient information
    """
    new_patient = {"patient_id": id, "attending_email": email,
                   "patient_age": age, "heart_rate": []}
    patient_db.append(new_patient)
    logging.info("New patient added to database: ID={}"
                 .format(new_patient["patient_id"]))
    return new_patient


def verify_new_patient_info(in_dict):
    """Verifies post request was made with correct format

    The input dictionary must have the appropriate data keys
    and types, or be convertible to correct types, to be added
    to the patient database.

    Args:
        in_dict (dict): input with new patient ID, physician email, and age

    Returns:
        str: if error, returns error message
        bool: if input verified, returns True
    """
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
    """Adds a heart rate to the patient's stored information

    Measured heart rates can be added to the patient's info
    to maintain proper records of patient heart activity
    over time.

    Args:
        None

    Returns:
        str: results of post request
        int: HTTP status code
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
        logging.info("Tachycardic heart rate of {} detected from patient "
                     "ID {} with attending email {}"
                     .format(in_dict["heart_rate"], in_dict["patient_id"],
                             email["to_email"]))
    if add_tach_to_db:
        return "Heart rate added to patient ID {}" \
                   .format(in_dict["patient_id"]), 200
    else:
        return "Unknown problem", 400


def verify_heart_rate_info(in_dict):
    """Verifies post request was made with correct format

    The input dictionary must have the appropriate data keys
    and types, or be convertible to correct types, to be added
    to the patient database.

    Args:
        in_dict (dict): input with patient ID and heart rate

    Returns:
        str: if error, returns error message
        bool: if input verified, returns True
    """
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
    """Checks if patient has previously been added to database

    The patient must be in the patient database to attach
    a heart rate measurement to their file.

    Args:
        id (int): patient ID

    Returns:
        bool: if ID present, True
    """
    for patient in patient_db:
        if patient["patient_id"] == id:
            return True
    return False


def add_hr_to_db(in_dict):
    """Adds heart rate to latest_hr key in patient database

    The heart rate must be affiliated with the correct
    patient ID in the database before it is checked for
    tachycardia.

    Args:
        in_dict (dict): input with patient ID and heart rate

    Returns:
        bool: if heart rate added to patient database, returns True
    """
    for patient in patient_db:
        if patient["patient_id"] == in_dict["patient_id"]:
            patient["latest_hr"] = in_dict["heart_rate"]
            return True
    return False


def is_tachycardic(in_dict):
    """Checks if heart rate measurement indicates tachycardia

    Tachycardia occurs when the heart beats too quickly. The
    threshold for tachycardia varies by age, decreasing from
    151 to 100 as age increases from 1 to older than 15 years.

    Args:
        in_dict (dict): input with patient ID and heart rate

    Returns:
        bool: if heart rate tachycardic, returns True
    """
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
    """Adds heart rate, status, and timestamp to patient info

    The heart rate is affiliated with status of tachycardia
    and the timestamp it was taken for proper record keeping
    and to trigger further action from the attending physician
    if necessary.

    Args:
        in_dict (dict): input with patient ID and heart rate
        tach (bool): True if latest heart rate indicates tachycardia

    Returns:
        bool: if heart rate, status, and timestamp added, returns True
    """
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
    """Composes email to send to attending if tachycardic

    If the patient is exhibiting symptoms of tachycardia,
    ie an increased heart rate, further action from the
    physician might be necessary. As such, the physician
    must be notified.

    Args:
        in_dict (dict): input with patient ID and heart rate

    Returns:
        dict: email to be sent to the physician
    """
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
    """Sends email to physician with patient details

    The attending physician must be alerted and provided
    with the relevant patient information in order to take
    action regarding tachycardia symptoms.

    Args:
        email (dict): email to be sent to physician

    Returns:
        str: message regarding send status of email
    """
    email_server = "http://vcm-7631.vm.duke.edu:5007/hrss/send_email"
    r = requests.post(email_server, json=email)
    if r.status_code != 200:
        return "Error: {} - {}".format(r.status_code, r.text)
    else:
        return "Success: {}".format(r.text)


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_latest_hr(patient_id):
    """Returns latest recorded heart rate from patient

    If requested, the most recent heart rate corresponding
    with the input patient ID is returned. The most recent
    heart rate can be used to check the current health
    status of the patient.

    Args:
        patient_id (int): patient ID for information requested

    Returns:
        str: if error, corresponding message
        dict: if available, latest heart rate, status, timestamp
        int: HTTP status code
    """
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
    """Returns all recorded heart rates from patient

    If requested, all recorded heart rates corresponding
    with the input patient ID are returned. The series of
    heart rates can be used to monitor changing health
    status over time.

    Args:
        patient_id (int): patient ID for information requested

    Returns:
        str: if error, corresponding message
        list: if available, all stored patient heart rates
        int: HTTP status code
    """
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
    """Returns average heart rate for given patient

    If requested, the average of all stored heart rates
    corresponding with the input patient ID is returned.
    Average heart rate can be used to check the health
    status of a patient from a period of time.

    Args:
        patient_id (int): patient ID for information requested

    Returns:
        str: if error, corresponding message
        int: if available, average heart rate of patient
        int: HTTP status code
    """
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
    """Verifies input ID is correct type and in database

    The input patient ID must be the appropriate data type,
    or be convertible to correct type, and be in the database
    to collect the corresponding heart rates.

    Args:
        patient_id (int): patient ID for information requested

    Returns:
        str: if error, corresponding message
        int: if correct type, patient ID
    """
    try:
        id = int(patient_id)
    except ValueError:
        return "Bad patient ID in URL"
    if is_patient_in_database(id) is False:
        return "Patient ID {} does not exist in database".format(id)
    return id


def generate_latest_hr(patient_id):
    """Generates most recent heart rate, status, and timestamp

    The most recent heart rate can be used to check the current
    health status of the patient, including whether or not the
    patient is tachycardic.

    Args:
        patient_id (int): patient ID for information requested

    Returns:
        str: if no heart rates stored for that patient
        dict: latest heart rate along with status and timestamp
    """
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
    """Generates list of all recorded heart rates for patient

    The series of heart rates can be used to monitor changing
    health status over time and allow the physician to make
    corresponding treatment decisions.

    Args:
        patient_id (int): patient ID for information requested

    Returns:
        str: if no heart rates stored for that patient
        list: all heart rates recorded from the patient
    """
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
    """Calculates the average from list of heart rates

    Average heart rate can be used to check the health
    status of a patient from a period of time.

    Args:
        hr_list (list): recorded patient heart rates

    Returns:
        int: average heart rate of stored values
    """
    avg_hr = round(statistics.mean(hr_list))
    return avg_hr


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def post_heart_rate_interval_avg():
    """Returns average heart rate for given patient from given time

    If requested, the average of stored heart rates from
    the given time corresponding with the input patient ID
    is returned. Average heart rate can be used to check the
    health status of a patient from a period of time.

    Args:
        None

    Returns:
        str: if error, corresponding message
        int: if available, average heart rate of patient since given time
        int: HTTP status code
    """
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
    """Verifies post request was made with correct format

    The input dictionary must have the appropriate data keys
    and types, or be convertible to correct types, to be elicit
    the correct patient heart rate data.

    Args:
        in_dict (dict): input with patient ID and datetime

    Returns:
        str: if error, returns error message
        bool: if input verified, returns True
    """
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
    """Generates list of heart rates from given time

    The series of heart rates can be used to monitor changing
    health status over time and allow the physician to make
    corresponding treatment decisions.

    Args:
        patient_id (int): patient ID for information requested
        sent_time (str): datetime string heart rates desired since

    Returns:
        str: error message if no heart rates stored
        list: heart rates recorded since desired time
    """
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
    app.run()

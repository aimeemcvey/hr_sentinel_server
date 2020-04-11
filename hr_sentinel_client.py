# hr_sentinel_client.py
import requests

server_name = "http://127.0.0.1:5000"


def add_patients():
    new_p = {"patient_id": 2, "attending_email": "dr@duke.edu",
             "patient_age": 24}
    r = requests.post(server_name + "/api/new_patient", json=new_p)
    if r.status_code != 200:
        print("Error: {} - {}".format(r.status_code, r.text))
    else:
        print("Success: {}".format(r.text))


def add_hr():
    new_hr = {"patient_id": 2, "heart_rate": 60}
    r = requests.post(server_name + "/api/heart_rate", json=new_hr)
    print(r.status_code)
    print(r.text)


def get_results():
    r = requests.get(server_name + "/api/status/2")
    if r.status_code != 200:
        print("Error {} - {}".format(r.status_code, r.text))
    else:
        print("Success: {}".format(r.text))


def get_hr_interval_avg():
    hr_interval = {"patient_id": 2,
                   "heart_rate_average_since": "2020-04-11 19:30:36"}
    r = requests.post(server_name + "/api/heart_rate/interval_average",
                      json=hr_interval)
    print(r.status_code)
    print(r.text)


if __name__ == "__main__":
    # add_patients()
    # add_hr()
    # get_results()
    get_hr_interval_avg()

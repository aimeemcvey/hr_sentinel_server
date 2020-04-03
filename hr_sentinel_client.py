# hr_sentinel_client.py
import requests

server_name = "http://127.0.0.1:5000"


def add_patients():
    new_p = {"patient_id": 1, "attending_email": "dr@duke.edu",
             "patient_age": 45}
    r = requests.post(server_name+"/api/new_patient", json=new_p)
    if r.status_code != 200:
        print("Error: {} - {}".format(r.status_code, r.text))
    else:
        print("Success: {}".format(r.text))


if __name__ == "__main__":
    add_patients()

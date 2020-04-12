# Heart Rate Sentinel Server [![Build Status](https://travis-ci.com/BME547-Spring2020/hr-sentinel-server-aimeemcvey.svg?token=uYZMqDdwHppZCbLZESzP&branch=master)](https://travis-ci.com/BME547-Spring2020/hr-sentinel-server-aimeemcvey)
This project is a centralized heart rate sentinel server. The server receives GET and POST requests from mock patient heart rate monitors that contain patient heart rate information over time. If a patient exhibits a tachycardic heart rate, the physician receives an email warning them of the situation. So if a new heart rate is received for a patient that is tachycardic, the email should be sent out at that time. 

## Overview

* `POST /api/new_patient` takes the following JSON to register add a new patient to the database when a heart rate monitor is checked out and attached to a patient:
  ```
  {
      "patient_id": 1,
      "attending_email": "dr_user_id@yourdomain.com", 
      "patient_age": 50, # in years
  }
  ```
  The patient_age and patient_age can be integers or number strings. After initialization, the server can accept future heart rate measurements and requests for the patient. The server also writes to the log file with the patient ID when a new patient is registered.

* `POST /api/heart_rate` takes the following JSON to add a heart rate to a patient:
  ```
  {
      "patient_id": 1,
      "heart_rate": 100
  }
  ```
  As with the `/api/new_patient` route, the patient_id and heart_rate may be sent as an integer or a number string. The sent heart rate measurement is stored in the record for the specified patient along with whether the measurement is or is not tachycardic and the datetime stamp of the measurement. If the posted heart rate is tachycardic for the specified patient and patient age, an e-mail is sent to the attending physician whose e-mail address was registered in the `api/new_patient` route with the patient_id, the tachycardic heart rate, and the date/time stamp of that heart rate. If the patient is tachycardic, the server also writes to the log file with the patient ID, the heart rate, and the attending physician e-mail.

* `GET /api/status/<patient_id>` returns a dictionary in a JSON string with the latest heart rate, tachycardia status, and date/time stamp for a specified patient:
  ```
  {
      "heart_rate": 100,
      "status":  "tachycardic" | "not tachycardic",
      "timestamp": "2018-03-09 11:00:36.372339"  
  }
  ```

* `GET /api/heart_rate/<patient_id>` returns a list of all the previous 
  heart rate measurements for that patient, as a list of integers.

* `GET /api/heart_rate/average/<patient_id>` returns the patient's 
  average heart rate, as an integer, of all measurements stored for 
  this patient.
 
* `POST /api/heart_rate/interval_average` takes a JSON as follows to return the average, as an integer, of all the heart rates posted for the specified patient since the given date/time: 
  ```
  {
      "patient_id": 1,
      "heart_rate_average_since": "2018-03-09 11:00:36.372339"
  }
  ```

All routes validate input data, ensuring that the appropriate keys and types in the JSON inputs exist and are correct. If the input is incorrect, a 400 error code is returned along with an error message.

## Server
The server is running at **vcm-13874.vm.duke.edu:5000**.

## License
MIT License

Copyright (c) [2020] [Aimee McVey]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
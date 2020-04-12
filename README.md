# Heart Rate Sentinel Server
This project is a centralized heart rate sentinel server. The server receives GET and POST requests from mock patient heart rate monitors that contain patient heart rate information over time. If a patient exhibits a tachycardic heart rate, the physician receives an email warning them of the situation. So if a new heart rate is received for a patient that is tachycardic, the email should be sent out at that time. 

The tachycardic calculation is based on age.
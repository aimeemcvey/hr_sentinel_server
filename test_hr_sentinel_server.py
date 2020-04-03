# test_hr_sentinel_server.py
import pytest


def test_add_patient_to_db():
    from hr_sentinel_server import add_patient_to_db
    answer = add_patient_to_db(3, "joeshmo@unc.edu", 53)
    expected = {"patient_id": 3, "attending_email": "joeshmo@unc.edu",
                "patient_age": 53}
    assert answer == expected

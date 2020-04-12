# test_hr_sentinel_server.py
import pytest
from datetime import datetime


def test_add_patient_to_db():
    from hr_sentinel_server import add_patient_to_db
    answer = add_patient_to_db(3, "joeshmo@unc.edu", 53)
    expected = {"patient_id": 3, "attending_email": "joeshmo@unc.edu",
                "patient_age": 53, "heart_rate": []}
    assert answer == expected


def test_verify_new_patient_info_good():
    from hr_sentinel_server import verify_new_patient_info
    in_dict = {"patient_id": 1, "attending_email": "yankeedoodle@nyu.edu",
               "patient_age": 1776}
    answer = verify_new_patient_info(in_dict)
    expected = True
    assert answer == expected


@pytest.mark.parametrize("in_dict, expected", [
    ({"patient_name": 1, "attending_email": "yankeedoodle@nyu.edu",
      "patient_age": 1776}, "patient_id key not found"),
    ({"patient_id": 1, "attending_name": "Yankee Doodle",
      "patient_age": 1776}, "attending_email key not found"),
    ({"patient_id": 1, "attending_email": "yankeedoodle@nyu.edu",
      "patient_year": 2020}, "patient_age key not found"),
])
def test_verify_new_patient_info_badkey(in_dict, expected):
    from hr_sentinel_server import verify_new_patient_info
    answer = verify_new_patient_info(in_dict)
    assert answer == expected


@pytest.mark.parametrize("in_dict, expected", [
    ({"patient_id": "1", "attending_email": "yankeedoodle@nyu.edu",
      "patient_age": "1776"}, True),
    ({"patient_id": 1, "attending_email": 24,
      "patient_age": 1776}, "attending_email value not correct type"),
    ({"patient_id": "one", "attending_email": "yankeedoodle@nyu.edu",
      "patient_age": 1776}, "patient_id value not correct type"),
])
def test_verify_new_patient_info_badtype(in_dict, expected):
    from hr_sentinel_server import verify_new_patient_info
    answer = verify_new_patient_info(in_dict)
    assert answer == expected


def test_verify_heart_rate_info_good():
    from hr_sentinel_server import verify_heart_rate_info
    in_dict = {"patient_id": 1, "heart_rate": 101}
    answer = verify_heart_rate_info(in_dict)
    expected = True
    assert answer == expected


@pytest.mark.parametrize("in_dict, expected", [
    ({"patient_name": 1, "heart_rate": 82}, "patient_id key not found"),
    ({"patient_id": 1, "hr": 64}, "heart_rate key not found"),
])
def test_verify_heart_rate_info_badkey(in_dict, expected):
    from hr_sentinel_server import verify_heart_rate_info
    answer = verify_heart_rate_info(in_dict)
    assert answer == expected


@pytest.mark.parametrize("in_dict, expected", [
    ({"patient_id": "1", "heart_rate": 73}, True),
    ({"patient_id": "1", "heart_rate": "101"}, True),
    ({"patient_id": "one", "heart_rate": 56},
     "patient_id value not correct type"),
    ({"patient_id": 2, "heart_rate": "high"},
     "heart_rate value not correct type"),
])
def test_verify_heart_rate_info_badtype(in_dict, expected):
    from hr_sentinel_server import verify_heart_rate_info
    answer = verify_heart_rate_info(in_dict)
    assert answer == expected


def test_is_patient_in_database_true():
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import is_patient_in_database
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    id = 12
    answer = is_patient_in_database(id)
    expected = True
    assert answer == expected


def test_is_patient_in_database_false():
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import is_patient_in_database
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    id = 13
    answer = is_patient_in_database(id)
    expected = False
    assert answer == expected


def test_add_hr_to_db():
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import add_hr_to_db
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    in_dict = {"patient_id": 12, "heart_rate": 75}
    answer = add_hr_to_db(in_dict)
    expected = True
    assert answer == expected


@pytest.mark.parametrize("in_dict, expected", [
    ({"patient_id": 5, "heart_rate": 120}, True),
    ({"patient_id": 5, "heart_rate": 100}, False),
])
def test_is_tachycardic(in_dict, expected):
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import add_hr_to_db
    from hr_sentinel_server import is_tachycardic
    add_patient_to_db(5, "srszn@jokes.com", 12)
    add_hr_to_db(in_dict)
    answer = is_tachycardic(in_dict)
    assert answer == expected


def test_add_tach_to_db():
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import add_tach_to_db
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    in_dict = {"patient_id": 12, "heart_rate": 75}
    answer = add_tach_to_db(in_dict, False)
    expected = True
    assert answer == expected


def test_compose_email():
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import add_tach_to_db
    from hr_sentinel_server import compose_email
    add_patient_to_db(7, "livelaughlove@hotmail.com", 54)
    in_dict = {"patient_id": 7, "heart_rate": 130}
    add_tach_to_db(in_dict, True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    answer = compose_email(in_dict)
    expected = {'from_email': 'ajm111@duke.edu', 'to_email':
                'livelaughlove@hotmail.com', 'subject':
                    'Urgent Tachycardia Alert', 'content':
                    'Patient 7 is tachycardic with HR of 130 at {}'
                        .format(timestamp)}
    assert answer == expected


@pytest.mark.parametrize("patient_id, expected", [
    (584393, 584393),
    ("six", "Bad patient ID in URL"),
    ("8943", "Patient ID 8943 does not exist in database")
])
def test_verify_id_input(patient_id, expected):
    from hr_sentinel_server import add_patient_to_db
    from hr_sentinel_server import verify_id_input
    add_patient_to_db(584393, "drdeath@hurt.com", 27)
    answer = verify_id_input(patient_id)
    assert answer == expected


@pytest.mark.parametrize("patient_id, expected", [
    (28594, {"heart_rate": 93, "status": "not tachycardic",
             "timestamp": '2020-04-11 00:00:54'}),
    (34857, "No heart rates in database")
])
def test_generate_latest_hr(patient_id, expected):
    from hr_sentinel_server import generate_latest_hr
    from hr_sentinel_server import add_patient_to_db
    patient = add_patient_to_db(28594, "drdeath@hurt.com", 85)
    patient["heart_rate"].append((83, 'not tachycardic',
                                  '2020-04-11 00:00:01'))
    patient["heart_rate"].append((85, 'not tachycardic',
                                  '2020-04-11 00:00:50'))
    patient["heart_rate"].append((93, 'not tachycardic',
                                  '2020-04-11 00:00:54'))
    add_patient_to_db(34857, "drdeath@hurt.com", 35)
    answer = generate_latest_hr(patient_id)
    assert answer == expected


@pytest.mark.parametrize("patient_id, expected", [
    (19283, [56, 64, 111]),
    (13857, "No heart rates in database")
])
def test_generate_all_hr(patient_id, expected):
    from hr_sentinel_server import generate_all_hr
    from hr_sentinel_server import add_patient_to_db
    patient = add_patient_to_db(19283, "drjones@med.com", 46)
    patient["heart_rate"].append((56, 'not tachycardic',
                                  '2020-04-11 14:00:01'))
    patient["heart_rate"].append((64, 'not tachycardic',
                                  '2020-04-11 14:01:50'))
    patient["heart_rate"].append((111, 'tachycardic',
                                  '2020-04-11 14:03:54'))
    add_patient_to_db(13857, "drjones@med.com", 23)
    answer = generate_all_hr(patient_id)
    assert answer == expected


@pytest.mark.parametrize("hr_list, expected", [
    ([56, 64, 111, 100, 94], 85),
    ([100, 103, 105, 121], 107),
    ([76, 84, 91, 81], 83)
])
def test_generate_avg_hr(hr_list, expected):
    from hr_sentinel_server import generate_avg_hr
    answer = generate_avg_hr(hr_list)
    assert answer == expected


@pytest.mark.parametrize("in_dict, expected", [
    ({"patient_id": "12847", "heart_rate_average_since": "2020-04-11 19:30:36"},
     True),
    ({"patiet_id": 12847, "heart_rate_average_since": "2020-04-11 19:30:36"},
     "patient_id key not found"),
    ({"patient_id": 12847, "heart_rate_average_since": 2020},
     "heart_rate_average_since value not correct type")
])
def test_verify_interval_info(in_dict, expected):
    from hr_sentinel_server import verify_interval_info
    answer = verify_interval_info(in_dict)
    assert answer == expected

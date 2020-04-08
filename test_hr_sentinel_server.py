# test_hr_sentinel_server.py
import pytest


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
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    from hr_sentinel_server import is_patient_in_database
    id = 12
    answer = is_patient_in_database(id)
    expected = True
    assert answer == expected


def test_is_patient_in_database_false():
    from hr_sentinel_server import add_patient_to_db
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    from hr_sentinel_server import is_patient_in_database
    id = 13
    answer = is_patient_in_database(id)
    expected = False
    assert answer == expected


def test_add_hr_to_db():
    from hr_sentinel_server import add_patient_to_db
    add_patient_to_db(12, "gthcgth@duke.edu", 91)
    from hr_sentinel_server import add_hr_to_db
    in_dict = {"patient_id": 12, "heart_rate": 75}
    answer = add_hr_to_db(in_dict)
    expected = True
    assert answer == expected

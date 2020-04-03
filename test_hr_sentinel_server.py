# test_hr_sentinel_server.py
import pytest


def test_add_patient_to_db():
    from hr_sentinel_server import add_patient_to_db
    answer = add_patient_to_db(3, "joeshmo@unc.edu", 53)
    expected = {"patient_id": 3, "attending_email": "joeshmo@unc.edu",
                "patient_age": 53}
    assert answer == expected

    # for i, key in enumerate(expected_keys):
    #     if key not in in_dict.keys():
    #         return "{} key not found".format(key)
    #     if type(in_dict[key]) is not expected_types[i]:
    #         if key == "patient_id" or key == "patient_age":
    #             try:
    #                 int(in_dict[key])
    #             except ValueError:
    #                 return "{} value not correct type".format(key)
    #         else:
    #             return "{} value not correct type".format(key)
    # return True


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

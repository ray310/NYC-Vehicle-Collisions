"""Tests for scrape_city_council functions."""

import src.scrape_city_council as scc


def test_parse_cc_member_name():
    """Name should come after hyphen and space."""
    test_cases = {
        "district 1 - Peter Griffin": "Peter Griffin",
        "district 1 -       Peter Griffin": "Peter Griffin",
        "district 1-Peter Griffin": None,
        "district 1 Peter Griffin": None,
    }
    for k, v in test_cases.items():
        assert scc.parse_cc_member_name(k) == v


def test_format_phone_number():
    """Phone number should be 123-456-7890 format."""
    test_cases = [
        {"area_code": "123", "first": "456", "second": "7890"},
    ]
    for t in test_cases:
        assert scc.format_phone_number(**t) == "123-456-7890"


def test_format_phone_number_no_exception():
    """Inputs that could cause an exception should be caught and None returned."""
    test_cases = [
        {"area_code": "12", "first": "456", "second": "7890"},
        {"area_code": "123", "first": "45", "second": "7890"},
        {"area_code": "123", "first": "456", "second": "789"},
        {"area_code": "abc", "first": "456", "second": "7890"},
        {"area_code": "123", "first": [4, 5, 6], "second": "7890"},
        {"area_code": "123", "first": "456", "second": [None, (2, 3), [3, 4], "2s"]},
        {"area_code": None, "first": None, "second": None},
        {"area_code": 123, "first": 456, "second": 7890},
    ]
    for t in test_cases:
        assert scc.format_phone_number(**t) is None


def test_parse_phone_number():
    """
    Phone number has 10 digits. Area code may have parentheses. Three parts
    of number may be separated by hyphens or spaces.
    """
    test_cases = {
        ("(111)222333 xyz-999_8887777 122-333-4444\n"): "122-333-4444",
        ("(111)222333 xyz-999#8887777 (212)-333-4444\n"): "212-333-4444",
        ("(111)222333 xyz-999/8887777 (221- 333 - 4444\n"): "221-333-4444",
        ("(111)222333 xyz-999>8887777 222) 133 - 4444\n"): "222-133-4444",
        ("(111)222333 xyz-999.8887777 222 - 313-4444\n"): "222-313-4444",
        ("(111)222333 xyz-999+8887777 222-331 - 4444\n"): "222-331-4444",
        ("(111)222333 xyz-999@8887777 222 333 1444\n"): "222-333-1444",
        ("(111)222333 xyz-999j8887777 222-333 4144\n"): "222-333-4144",
        ("(111)222333 xyz-999a8887777 222 333-4414\n"): "222-333-4414",
    }
    for k, v in test_cases.items():
        assert scc.parse_phone_number(k) == v


def test_parse_address():
    """
    Address should be up to three lines. Third line should not be parsed if it
    contains a valid phone number.
    """
    test_cases = {
        "31 Spooner St.\nQuahog RI 02940\nPhone: 212-555-5555": "31 Spooner St.\nQuahog RI 02940",
        "31 Spooner St.\nTime Machine\nQuahog RI 02940\nPhone: 212-555-5555": "31 Spooner St.\nTime Machine\nQuahog RI 02940",
        "31 Spooner St.\nMeg's Room\nQuahog RI 02940": "31 Spooner St.\nMeg's Room\nQuahog RI 02940",
        "31 Spooner St.\r\nMeg's Room\r\nQuahog RI 02940": "31 Spooner St.\nMeg's Room\nQuahog RI 02940",
        "31 Spooner St.\r\nMeg's Room\r\n(212)-55-5555": "31 Spooner St.\nMeg's Room\n(212)-55-5555",
    }
    for k, v in test_cases.items():
        assert scc.parse_address(k) == v


def test_parse_cc_email():
    """Correct email address should come after mailto:."""
    district_num = 1
    test_cases = [
        ({"href": f"mailto:District{district_num}@council.nyc.gov"}, f"District{district_num}@council.nyc.gov"),
        ({"href": f"mailto:district{district_num}@council.nyc.gov"}, f"district{district_num}@council.nyc.gov"),
        ({"href": "mailto:gquagmire@council.nyc.gov"}, "gquagmire@council.nyc.gov"),
        ({"href": "mailtogquagmire@council.nyc.gov"}, f"district{district_num}@council.nyc.gov"),
        ({"href": "adamwest@council.nyc.gov"}, f"district{district_num}@council.nyc.gov"),  # no mailto
        ({"href": "mailto:adamwest@council.nyc.com"}, f"district{district_num}@council.nyc.gov"),  # .com
        (None, f"district{district_num}@council.nyc.gov")
    ]
    for case in test_cases:
        assert scc.parse_cc_email(case[0], district_num) == case[1]

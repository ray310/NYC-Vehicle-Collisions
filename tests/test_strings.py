"""Tests for strings utility functions."""

import pandas as pd
import src.strings


def test_insert_line_breaks_space_before_equal_index():
    """Line break should be inserted at the last space <= the index value provided."""
    test_cases = {
        ("One space", 3): "One\nspace",
        ("this, has. three! spaces", 16): "this, has.\nthree! spaces",
        ("this, has. three! spaces", 17): "this, has. three!\nspaces",
    }
    for k, v in test_cases.items():
        assert src.strings.insert_line_break(k[0], k[1]) == v


def test_insert_line_breaks_space_after_index():
    """Input string should return the same string if there are only spaces
    after input index."""
    s = "This,has '`spaces"
    assert src.strings.insert_line_break(s, 7) == s


def test_insert_line_breaks_space_no_spaces():
    """Input string should return the same string if there are no spaces."""
    s = "This,has.no'`spaces"
    assert src.strings.insert_line_break(s, len(s)) == s


def test_insert_line_breaks_empty_string():
    """Empty string should return empty string."""
    s = ""
    assert src.strings.insert_line_break(s, 1) == s


def test_length_after_line_break_no_spaces():
    """Input string with no spaces will return length of string."""
    s = "there,are.no'spaces"
    assert src.strings.length_after_line_break(s) == len(s)


def test_length_after_line_break():
    """Function should return the length of the longest line if an optimal line
    break were inserted."""
    test_cases = {"ab c de": 4, "ab cd ef g hijklmno": 10}
    for k, v in test_cases.items():
        assert src.strings.length_after_line_break(k) == v


def test_get_space_indices_has_spaces():
    """String input should return list of indices for spaces."""
    test_cases = {
        " Three spaces ": [0, 6, 13],
        "Comma,not space": [9],
        "Period.not space": [10],
    }
    for k, v in test_cases.items():
        assert src.strings.get_space_indices(k) == v


def test_get_space_indices_empty_string():
    """Empty string should return empty list."""
    assert src.strings.get_space_indices("") == []


def test_get_space_indices_not_string():
    """Non-string inputs should return None."""
    values = [[], (), {}, None, 7, 7.1, ["strings"]]
    for val in values:
        assert src.strings.get_space_indices(val) is None


def test_add_line_breaks_list():
    """List of strings should be list of strings with correct line breaks added."""
    input_arr = ["abcd ef ghijk", "abcdefgh", "abcdef g hijklm"]
    output_arr = ["abcd ef\nghijk", "abcdefgh", "abcdef g\nhijklm"]
    assert src.strings.add_line_breaks(input_arr) == output_arr


def test_add_line_breaks_pd_series():
    """Pd.Series of strings should list of strings with correct line breaks added."""
    input_arr = pd.Series(["abcd ef ghijk", "abcdefgh", "abcdef g hijklm"])
    output_arr = ["abcd ef\nghijk", "abcdefgh", "abcdef g\nhijklm"]
    assert src.strings.add_line_breaks(input_arr) == output_arr

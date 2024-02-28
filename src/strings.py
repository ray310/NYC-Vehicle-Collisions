""" String formatting functions."""

from typing import Iterable
import numpy as np


def add_line_breaks(str_arr: Iterable):
    """Returns list of strings with optimal line break inserted"""
    max_line_length = max(length_after_line_break(s) for s in str_arr)
    return [insert_line_break(s, max_line_length) for s in str_arr]


def insert_line_break(s: str, idx: int):
    """Returns new string with line break inserted at or before index, idx"""
    spaces = [x for x in get_space_indices(s) if x <= idx]
    if not spaces:
        return s
    line_break = max(spaces)
    new_str = list(s)
    new_str[line_break] = "\n"
    return "".join(new_str)


def length_after_line_break(s: str):
    """Returns length of longest line after replacing space with line break
    near string mid-point."""
    spaces = get_space_indices(s)
    if not spaces:
        return len(s)
    mid = (len(s) - 1) / 2
    line_break_idx = spaces[np.argmin([abs(x - mid) for x in spaces])]
    return max(line_break_idx, len(s) - line_break_idx - 1)


def get_space_indices(s: str):
    """Returns list of indices for spaces in a string"""
    if not isinstance(s, str):
        return None
    return [idx for idx, c in enumerate(s) if c == " "]

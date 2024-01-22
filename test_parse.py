import parse
import numpy as np

def test_simple_eval():

    a = "5 * 2 + 3"
    expected = 13
    out = parse.parse_string(a)
    answer = parse.evaluate_expression(out, {})
    assert answer == expected

def test_order_swap():
    a = "5 * 2 + 3"
    expected = 13
    out = parse.parse_string(a)
    expected = parse.evaluate_expression(out, {})
    b = a[::-1]
    out_2 = parse.parse_string(b)
    answer = parse.evaluate_expression(out_2, {})
    
    assert answer == expected

def test_extended():
    a = "5 * 2 + 3 * 4 + 22-5"
    out = parse.parse_string(a)
    excepted = 10 + 12 + 17
    answer = parse.evaluate_expression(out, {})
    assert answer == excepted

def test_array_access():
    a = "a[5] + 3*c[7*i + 3]"
    vals = {"a": np.arange(6)*5, "c": np.arange(15), "i": 1}
    out = parse.parse_string(a)
    excepted = 55
    answer = parse.evaluate_expression(out, vals)

    assert answer == excepted

def test_array_access_pemdas():
    a = "a[5] * 3 + c[7*i + 3]"
    vals = {"a": np.arange(6)*5, "c": np.arange(15), "i": 1}
    out = parse.parse_string(a)
    excepted = 75 + 10
    answer = parse.evaluate_expression(out, vals)

    assert answer == excepted

def test_array_array_access():
    a = "a[c[5-3*i]]"
    vals = {"a": np.arange(6)*5, "c": np.arange(15), "i": 1}
    out = parse.parse_string(a)
    excepted = 10
    answer = parse.evaluate_expression(out, vals)
    assert answer == excepted

def test_array_array_with_after_access():
    a = "a[c[5-3*i]] + 15"
    vals = {"a": np.arange(6)*5, "c": np.arange(15), "i": 1}
    out = parse.parse_string(a)
    excepted = 10 + 15
    answer = parse.evaluate_expression(out, vals)
    assert answer == excepted
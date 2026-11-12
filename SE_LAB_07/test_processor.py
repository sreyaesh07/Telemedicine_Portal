
from hypothesis import given, strategies as st
from processor import (
    parse_season_pass_validity,
    compute_trail_gradient,
    calculate_lift_access_tier
)


@given(st.text() | st.none())
def test_parse_season_pass_validity_no_crash(s):
    try:
        parse_season_pass_validity(s)
    except Exception as e:
        assert False, f"Date function crashed with input {s!r}: {e}"


@given(st.text() | st.none())
def test_compute_trail_gradient_safe(s):
    try:
        compute_trail_gradient(s)
    except Exception as e:
        assert False, f"Gradient function crashed with input {s!r}: {e}"


@given(st.text() | st.none())
def test_calculate_lift_access_tier_safe(s):
    try:
        calculate_lift_access_tier(s)
    except Exception as e:
        assert False, f"Lift tier function crashed with input {s!r}: {e}"

"""Lab 6 - Branch coverage tests for ski_resort_pass.py"""
import pytest
from ski_resort_pass import process_resort_bookings, check_chairlift_anemometer


def make_group(duration="full_day", skiers=None, locker=False, active=True):
    return {
        "is_active": active,
        "duration": duration,
        "includes_lodge_locker": locker,
        "skiers": skiers if skiers is not None else [],
    }


def skier(age=30, gear=False, blackout=False):
    return {"age": age, "gear_rental": gear, "blackout_override": blackout}


# ---------- Example test (from starter) ----------
def test_single_adult_full_day():
    result = process_resort_bookings([make_group("full_day", [skier(30)])], 15.0)
    assert result["total_revenue"] == 80.0
    assert result["status"] == "COMPLETED"


# ---------- Input validation (line 2: both operands of 'or') ----------
def test_groups_not_a_list_raises():
    with pytest.raises(ValueError):
        process_resort_bookings("not a list", 10.0)


def test_negative_facility_fee_raises():
    with pytest.raises(ValueError):
        process_resort_bookings([], -0.01)


def test_zero_fee_and_empty_list_is_valid():
    assert process_resort_bookings([], 0.0) == {"total_revenue": 0.0, "status": "ZERO_SALES"}


# ---------- Group-level branches ----------
def test_inactive_group_skipped():
    assert process_resort_bookings([make_group(active=False, skiers=[skier()])], 5.0)["status"] == "ZERO_SALES"


def test_missing_keys_use_defaults():
    # no is_active -> inactive by default
    assert process_resort_bookings([{}], 5.0)["status"] == "ZERO_SALES"
    # no duration -> defaults to full_day; no skiers -> empty
    result = process_resort_bookings([{"is_active": True}], 5.0)
    assert result["status"] == "ZERO_SALES"


@pytest.mark.parametrize("duration, expected", [
    ("season", 300.0),
    ("full_day", 80.0),
    ("half_day", 50.0),
])
def test_duration_rates(duration, expected):
    result = process_resort_bookings([make_group(duration, [skier(30)])], 0.0)
    assert result["total_revenue"] == expected


def test_unknown_duration_rejected():
    result = process_resort_bookings([make_group("weekly", [skier(30)])], 0.0)
    assert result["status"] == "ZERO_SALES"


# ---------- Skier-level branches ----------
@pytest.mark.parametrize("age, expected", [
    (-5, 0.0),     # invalid
    (0, 0.0),      # boundary: invalid
    (1, 48.0),     # child
    (11, 48.0),    # child upper boundary
    (12, 80.0),    # adult lower boundary
    (64, 80.0),    # adult upper boundary
    (65, 56.0),    # senior boundary
    (90, 56.0),    # senior
])
def test_age_categories_full_day(age, expected):
    result = process_resort_bookings([make_group("full_day", [skier(age)])], 0.0)
    assert result["total_revenue"] == expected


def test_skier_missing_age_defaults_invalid():
    result = process_resort_bookings([make_group("full_day", [{}])], 0.0)
    assert result["status"] == "ZERO_SALES"


def test_blackout_override_full_day_half_price():
    result = process_resort_bookings([make_group("full_day", [skier(30, blackout=True)])], 0.0)
    assert result["total_revenue"] == 40.0


def test_blackout_override_half_day_voids_group_and_stops():
    # The group total is reset and the loop breaks: the 3rd skier is never priced.
    skiers = [skier(30), skier(30, blackout=True), skier(30)]
    result = process_resort_bookings([make_group("half_day", skiers, locker=True)], 10.0)
    # group_total reset to 0, then locker fee 10 is still added
    assert result == {"total_revenue": 10.0, "status": "COMPLETED"}


def test_gear_rental_true_and_false():
    with_gear = process_resort_bookings([make_group("full_day", [skier(30, gear=True)])], 0.0)
    without_gear = process_resort_bookings([make_group("full_day", [skier(30)])], 0.0)
    assert with_gear["total_revenue"] == 115.0
    assert without_gear["total_revenue"] == 80.0


def test_blackout_with_gear_rental_adds_gear():
    result = process_resort_bookings([make_group("season", [skier(30, gear=True, blackout=True)])], 0.0)
    assert result["total_revenue"] == 150.0 + 35.0


def test_lodge_locker_true_and_false():
    with_locker = process_resort_bookings([make_group("full_day", [skier(30)], locker=True)], 15.0)
    no_locker = process_resort_bookings([make_group("full_day", [skier(30)], locker=False)], 15.0)
    assert with_locker["total_revenue"] == 95.0
    assert no_locker["total_revenue"] == 80.0


def test_multiple_groups_accumulate():
    groups = [make_group("full_day", [skier(30)]), make_group("half_day", [skier(30)])]
    assert process_resort_bookings(groups, 0.0)["total_revenue"] == 130.0


# ---------- Final status branches ----------
def test_audit_review_more_than_four_rejections():
    skiers = [skier(0) for _ in range(5)] + [skier(30)]
    result = process_resort_bookings([make_group("full_day", skiers)], 0.0)
    assert result == {"total_revenue": 80.0, "status": "AUDIT_REVIEW"}


def test_exactly_four_rejections_is_not_audit():
    skiers = [skier(0) for _ in range(4)] + [skier(30)]
    result = process_resort_bookings([make_group("full_day", skiers)], 0.0)
    assert result["status"] == "COMPLETED"


def test_zero_sales_status():
    assert process_resort_bookings([make_group("full_day", [skier(0)])], 0.0)["status"] == "ZERO_SALES"


# ---------- check_chairlift_anemometer ----------
def test_anemometer_none_and_empty():
    assert check_chairlift_anemometer([]) == "NO_DATA"
    assert check_chairlift_anemometer(None) == "NO_DATA"


def test_anemometer_two_consecutive_gusts_suspend():
    assert check_chairlift_anemometer([[10, 50, 60]]) == "SUSPEND_LIFT"


def test_anemometer_streak_reset_is_safe():
    assert check_chairlift_anemometer([[50, 10, 50]]) == "SAFE_OPERATION"


def test_anemometer_exactly_45_is_not_a_gust():
    assert check_chairlift_anemometer([[45, 45, 45]]) == "SAFE_OPERATION"


def test_anemometer_empty_lift_then_second_lift_triggers():
    assert check_chairlift_anemometer([[], [46, 46]]) == "SUSPEND_LIFT"


def test_anemometer_streak_does_not_carry_across_lifts():
    assert check_chairlift_anemometer([[50], [50]]) == "SAFE_OPERATION"
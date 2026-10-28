"""Lab 6 - Line (code) coverage tests for ski_resort_pass.py"""
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
    groups = [make_group("full_day", [skier(30)])]
    result = process_resort_bookings(groups, 15.0)
    assert result["total_revenue"] == 80.0
    assert result["status"] == "COMPLETED"


# ---------- process_resort_bookings ----------
def test_invalid_groups_type_raises():
    with pytest.raises(ValueError):
        process_resort_bookings("not a list", 10.0)


def test_negative_facility_fee_raises():
    with pytest.raises(ValueError):
        process_resort_bookings([], -1.0)


def test_inactive_group_skipped_gives_zero_sales():
    result = process_resort_bookings([make_group(active=False)], 10.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_season_child_senior_gear_and_locker():
    # season rate 300: child 12<age -> 0.6*300=180, senior 0.7*300=210,
    # adult 300 + gear 35, locker fee 20
    skiers = [skier(8), skier(70), skier(30, gear=True)]
    result = process_resort_bookings([make_group("season", skiers, locker=True)], 20.0)
    assert result["total_revenue"] == 180.0 + 210.0 + 335.0 + 20.0
    assert result["status"] == "COMPLETED"


def test_half_day_adult():
    result = process_resort_bookings([make_group("half_day", [skier(30)])], 0.0)
    assert result["total_revenue"] == 50.0


def test_unknown_duration_rejected():
    result = process_resort_bookings([make_group("weekly", [skier(30)])], 0.0)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_invalid_age_rejected():
    result = process_resort_bookings([make_group("full_day", [skier(0)])], 0.0)
    assert result["status"] == "ZERO_SALES"


def test_blackout_override_full_day_half_price():
    result = process_resort_bookings([make_group("full_day", [skier(30, blackout=True)])], 0.0)
    assert result["total_revenue"] == 40.0


def test_blackout_override_half_day_voids_group():
    skiers = [skier(30), skier(30, blackout=True), skier(30)]
    result = process_resort_bookings([make_group("half_day", skiers)], 0.0)
    assert result["status"] == "ZERO_SALES"


def test_audit_review_when_more_than_four_rejections():
    skiers = [skier(0) for _ in range(5)] + [skier(30)]
    result = process_resort_bookings([make_group("full_day", skiers)], 0.0)
    assert result == {"total_revenue": 80.0, "status": "AUDIT_REVIEW"}


# ---------- check_chairlift_anemometer ----------
def test_anemometer_no_data():
    assert check_chairlift_anemometer([]) == "NO_DATA"


def test_anemometer_suspend_on_two_consecutive_gusts():
    assert check_chairlift_anemometer([[10, 50, 60]]) == "SUSPEND_LIFT"


def test_anemometer_safe_when_gust_streak_reset():
    assert check_chairlift_anemometer([[50, 10, 50]]) == "SAFE_OPERATION"

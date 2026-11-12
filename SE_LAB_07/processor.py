
from datetime import datetime
import math


def parse_season_pass_validity(date_str):
    try:
        if not isinstance(date_str, str):
            return None

        date_str = date_str.strip()

        # Check date format and validate actual calendar date
        expiry_date = datetime.strptime(date_str, "%Y/%m/%d")

        year = expiry_date.year
        month = expiry_date.month
        day = expiry_date.day

        valid = year >= 2026

        return (
            f"Pass Expiry: {year:04d}-{month:02d}-{day:02d} "
            f"({'VALID' if valid else 'EXPIRED'})"
        )

    except (ValueError, TypeError, OverflowError):
        return None


def compute_trail_gradient(elevation_str):
    try:
        if not isinstance(elevation_str, str):
            return None

        # Input must contain exactly two values
        parts = elevation_str.split(':')

        if len(parts) != 2:
            return None

        drop = float(parts[0].strip())
        distance = float(parts[1].strip())

        # Reject infinity, NaN, negative drop and invalid distance
        if not math.isfinite(drop) or not math.isfinite(distance):
            return None

        if drop < 0 or distance <= 0:
            return None

        gradient_pct = (drop / distance) * 100.0

        return round(gradient_pct, 2)

    except (ValueError, TypeError, OverflowError, ZeroDivisionError):
        return None


def calculate_lift_access_tier(zone_code):
    try:
        if not isinstance(zone_code, str):
            return None

        prefix = zone_code.strip().upper()[:3]

        zone_rates = {
            "BEG": 35.0,
            "INT": 60.0,
            "ADV": 85.0,
            "ALL": 110.0
        }

        # Prevent KeyError for unknown zones
        return zone_rates.get(prefix)

    except (ValueError, TypeError, AttributeError):
        return None


def main():
    print("==== Running parse_season_pass_validity ====")

    d_input = input("Enter pass expiry (YYYY/MM/DD): ")
    result = parse_season_pass_validity(d_input)
    print(result if result is not None else "Invalid date input")

    print("\n==== Running compute_trail_gradient ====")

    e_input = input("Enter drop:distance (e.g. 250:1000): ")
    result = compute_trail_gradient(e_input)
    print("Gradient %:", result if result is not None else "Invalid input")

    print("\n==== Running calculate_lift_access_tier ====")

    z_input = input("Enter zone code (e.g. BEG, INT, ALL): ")
    result = calculate_lift_access_tier(z_input)
    print("Lift Pass Price: $", result if result is not None else "Invalid zone")


if __name__ == "__main__":
    main()

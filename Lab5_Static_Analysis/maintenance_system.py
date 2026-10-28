"""Warehouse asset maintenance registry."""
import json
import tempfile
from datetime import datetime, timedelta

# Global state
assets = {}
SERVICE_INTERVAL_DAYS = 90

def register_asset(asset_id, machine_type, logs=None):
    """Register an asset with today's date as its last service date."""
    if logs is None:
        logs = []
    assets[asset_id] = {"type": machine_type, "last_service": datetime.now().strftime("%Y-%m-%d")}
    logs.append(asset_id)
    print("Registered", asset_id, "- total registrations this run:", len(logs))

def update_service_date(asset_id, date):
    """Update the last service date of an existing asset."""
    try:
        assets[asset_id]["last_service"] = date
    except KeyError:
        print("Could not update", asset_id)

def due_for_inspection():
    """Return the IDs of assets whose inspection is overdue."""
    due = []
    for asset_id, info in assets.items():
        last = datetime.strptime(info["last_service"], "%Y-%m-%d")
        if datetime.now() - last > timedelta(days=SERVICE_INTERVAL_DAYS):
            due.append(asset_id)
    return due

def change_interval(days):
    """Change the service interval in days."""
    global SERVICE_INTERVAL_DAYS  # pylint: disable=global-statement
    SERVICE_INTERVAL_DAYS = days

def export_service_report(file="maintenance.json"):
    """Write all assets to a JSON report file."""
    with open(file, "w", encoding="utf-8") as report:
        report.write(json.dumps(assets, indent=2))
    print("Report written to " + file)

def write_scratch_copy():
    """Write a temporary JSON copy of the assets."""
    with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
        tmp.write(json.dumps(assets))
        path = tmp.name
    print("Scratch copy at", path)

def print_alerts():
    """Print an alert for every overdue asset."""
    for asset_id in due_for_inspection():
        print("ALERT: inspection overdue for", asset_id, assets[asset_id]["type"])

def main():
    """Run the demo."""
    register_asset("FL-01", "Forklift")
    register_asset("CV-07", "Conveyor")
    register_asset("", "Pallet Jack")
    register_asset("FL-01", "Crane")
    update_service_date("FL-01", "2025-01-15")
    update_service_date("XX-99", "2025-02-01")
    change_interval(-30)
    d = input("Last service date for CV-07 (YYYY-MM-DD, Enter to skip): ")
    if d:
        update_service_date("CV-07", d)
    if not assets:
        raise ValueError("no assets")
    print_alerts()
    export_service_report()
    write_scratch_copy()

main()

# logger.py
import csv
import os
from datetime import datetime

class TrialLogger:
    def __init__(self, filepath="trials.csv"):
        self.filepath = filepath
        self.fieldnames = [
            "timestamp_iso",
            "trial_id",
            "group",
            "condition",
            "blink_time_s",
            "valid",
            "note",
        ]
        self._ensure_header()
        print(f"TrialLogger writing to: {os.path.abspath(self.filepath)}")

    def _ensure_header(self):
        # create file with header if it doesn't exist yet
        if not os.path.exists(self.filepath) or os.path.getsize(self.filepath) == 0:
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

    def append(self, result: dict):
        """
        result should contain keys matching fieldnames (extra keys are ignored).
        """
        row = {k: result.get(k, "") for k in self.fieldnames}
        row["timestamp_iso"] = row["timestamp_iso"] or datetime.now().isoformat(timespec="seconds")

        with open(self.filepath, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)
            f.flush()

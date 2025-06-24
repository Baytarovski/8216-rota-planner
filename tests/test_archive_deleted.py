import types
import builtins

import sys

# Provide a dummy streamlit module
sys.modules['streamlit'] = types.SimpleNamespace(secrets={}, cache_data=types.SimpleNamespace(clear=lambda: None))
sys.modules['gspread'] = types.SimpleNamespace()
sys.modules['google.oauth2.service_account'] = types.SimpleNamespace(Credentials=types.SimpleNamespace(from_service_account_info=lambda info, scopes=None: None))

import os

# Ensure the repository root is on the Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

import core.data_utils as data_utils

class FakeSheet:
    def __init__(self, rows=None):
        self.rows = rows or []
    def get_all_values(self):
        return [list(r) for r in self.rows]
    def append_row(self, row):
        self.rows.append(list(row))
    def clear(self):
        self.rows = []


def test_delete_and_archive_rota():
    week_key = "2025-01-06"
    header = ["week_start", "day"] + data_utils.POSITIONS
    rows = [
        header,
        [week_key, "Monday", "A", "H", "B", "C", "D", "E"],
        [week_key, "Tuesday", "A2", "H2", "B2", "C2", "D2", "E2"],
        ["2025-01-13", "Monday", "X", "H", "Y", "Z", "W", "Q"],
    ]
    sheet = FakeSheet(rows)
    deleted_sheet = FakeSheet([])

    original_get_sheet = data_utils.get_sheet
    original_get_deleted = data_utils.get_deleted_sheet
    data_utils.get_sheet = lambda: sheet
    data_utils.get_deleted_sheet = lambda: deleted_sheet

    try:
        deleted = data_utils.delete_rota(week_key)
        data_utils.archive_deleted_rota(week_key, deleted, "admin")
    finally:
        data_utils.get_sheet = original_get_sheet
        data_utils.get_deleted_sheet = original_get_deleted

    assert week_key not in [r[0] for r in sheet.rows if r]
    assert deleted_sheet.rows[0] == ["week_start", "day"] + data_utils.POSITIONS + ["admin_users"]
    assert deleted_sheet.rows[1][-1] == "admin"
    assert len(deleted_sheet.rows) == 1 + len(deleted)


import sys
import importlib
import types
import random
import os

# Provide a dummy streamlit module so algorithm can be imported without the real package
sys.modules['streamlit'] = types.SimpleNamespace(cache_data=types.SimpleNamespace(clear=lambda: None))

# Ensure the repository root is on the Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from core import algorithm
importlib.reload(algorithm)

POSITIONS = ["CAR1", "CAR2", "OFFAL", "FCI", "OFFLINE"]


def test_generate_rota_success():
    random.seed(0)
    daily_workers = {
        "Monday": ["A", "B", "C", "D", "E"],
        "Tuesday": ["A", "B", "C", "D", "E"],
        "Wednesday": ["A", "B", "C", "D", "E"],
        "Thursday": ["A", "B", "C", "D", "E"],
        "Friday": ["A", "B", "C", "D", "E"],
    }
    daily_heads = {day: "F" for day in daily_workers}
    rotas = {}
    inspectors = ["A", "B", "C", "D", "E", "F"]
    week_key = "2025-01-06"

    rota = algorithm.generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key)

    assert set(rota.keys()) == set(daily_workers.keys())
    role_usage = {}
    for day, assignments in rota.items():
        assert assignments["HEAD"] == "F"
        workers = [assignments[p] for p in POSITIONS]
        assert len(set(workers)) == len(workers)
        for pos in POSITIONS:
            worker = assignments[pos]
            assert worker in daily_workers[day]
            key = (worker, pos)
            assert key not in role_usage
            role_usage[key] = True


def test_generate_rota_missing_workers():
    random.seed(0)
    daily_workers = {
        "Monday": ["A", "B", "C", "D"],
    }
    daily_heads = {"Monday": "E"}
    rotas = {}
    inspectors = ["A", "B", "C", "D", "E"]
    week_key = "2025-01-06"

    algorithm.DEFAULT_ATTEMPTS = 10
    rota = algorithm.generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key)
    assert isinstance(rota, dict)
    assert "error" in rota


def test_generate_rota_repeated_workers():
    random.seed(0)
    daily_workers = {
        "Monday": ["A", "A", "B", "B", "C"],
    }
    daily_heads = {"Monday": "D"}
    rotas = {}
    inspectors = ["A", "B", "C", "D"]
    week_key = "2025-01-06"

    algorithm.DEFAULT_ATTEMPTS = 10
    rota = algorithm.generate_rota(daily_workers, daily_heads, rotas, inspectors, week_key)
    assert isinstance(rota, dict)
    assert "error" in rota

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from dashboard.helpers import str_in_clause, int_in_clause


def test_str_in_clause_multiple():
    assert str_in_clause(["Credit card", "Checking"]) == "('Credit card', 'Checking')"


def test_str_in_clause_single():
    assert str_in_clause(["Prepaid card"]) == "('Prepaid card')"


def test_str_in_clause_escapes_single_quotes():
    assert str_in_clause(["it's"]) == "('it''s')"


def test_int_in_clause_multiple():
    assert int_in_clause([2023, 2024]) == "(2023, 2024)"


def test_int_in_clause_single():
    assert int_in_clause([2024]) == "(2024)"

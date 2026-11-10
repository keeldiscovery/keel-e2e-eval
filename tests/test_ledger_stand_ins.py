"""The stand-ins' own guards (`stack/ledger.py`), moved here from `tests/test_contacts_marks.py` by spec 150 when the
contacts leg and its tests went: the stand-ins stay (the interviewer leg's `e2e-eval:044:`, the open-link leg's
`e2e-eval:092:`), so the ledger is still never reached on the remote profile and no value is ever spliced into its SQL."""

from __future__ import annotations

import ast
import inspect
import uuid

import pytest

from stack import ledger


class _Remote:
    is_remote = True


@pytest.mark.parametrize("call", [lambda c: ledger.founder_account(c, "sub"),
                                  lambda c: ledger.stand_in_keels_door(c, str(uuid.uuid4()), "r"),
                                  lambda c: ledger.stand_in_balance(c, str(uuid.uuid4()), "r", to=20),
                                  lambda c: ledger.restore_own_door(c, str(uuid.uuid4()), "r")])
def test_the_ledger_is_never_reached_on_the_remote_profile(call):
    with pytest.raises(ledger.LedgerUnavailable, match="remote"):
        call(_Remote())


def test_no_value_is_spliced_into_the_ledgers_sql():
    source = inspect.getsource(ledger)
    tree = ast.parse(source)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", "") in ("_psql", "_json")]
    assert len(calls) >= 8
    for call in calls:
        sql = call.args[1]
        literal = isinstance(sql, ast.Constant) or (
            isinstance(sql, ast.BinOp) and all(isinstance(x, ast.Constant) for x in (sql.left, sql.right)))
        wrapped = isinstance(sql, ast.JoinedStr) and [v.value.id for v in sql.values
                                                     if isinstance(v, ast.FormattedValue)] == ["select"]
        assert literal or wrapped, ast.unparse(sql)
    assert source.count("UPDATE founder_account") == 2                    # the door, and its reversal
    with pytest.raises(ledger.LedgerUnavailable):
        ledger.rows(type("Local", (), {"is_remote": False})(), "1; DROP TABLE credit_ledger")

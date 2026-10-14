import itertools

import pytest

from frontend.Planner import Planner

# Messages hardcoded in the program
M_RANGE = "Please enter a number from 0 - 6"
M_NOTINT = "valid number"
MON = "Month does not exist"
DAY = "Day does not exist"
HR = "Illegal hour"
ORDER = "Meeting starts before it ends"
ROOM = "Requested room does not exist"
EMP = "Requested employee does not exist"
BOOK = "Meeting is now booked!"
VAC = "Vacation is now booked!"


def run(monkeypatch, capsys, inputs):
    """Feed inputs to main_menu. When they run out, the menu receives '0' and exits."""
    feed = itertools.chain(inputs, itertools.repeat("0"))
    calls = {"n": 0}

    def fake_input(self, _prompt):
        calls["n"] += 1
        if calls["n"] > 300:
            raise RuntimeError("Program is stuck re-prompting")
        return next(feed)

    monkeypatch.setattr(Planner, "input_output", fake_input)
    with pytest.raises(SystemExit):
        Planner().main_menu()
    return capsys.readouterr().out


def check(monkeypatch, capsys, inputs, must=(), must_not=()):
    out = run(monkeypatch, capsys, inputs)
    for text in must:
        assert text in out, f"Expected {text!r} in output:\n{out}"
    for text in must_not:
        assert text not in out, f"Did not expect {text!r} in output:\n{out}"


# ---------- input builders (prompt order taken from Planner.py) ----------
def meet(m="8", d="13", s="9", e="10", room="JO18.330",
         people=("Justin Gardener",), desc="Project review"):
    """Full schedule flow. Attendees are followed by 'done'."""
    return ["6", m, d, s, e, room, *people, "done", desc]


def meet_time(m="8", d="13", s="9", e="10"):
    """Schedule flow that stops at the date and time checks (program returns to the menu)."""
    return ["6", m, d, s, e]


def vac(name="Mike Smith", sm="8", sd="13", em="8", ed="20"):
    return ["5", name, sm, sd, em, ed]


def avail(menu, m="8", d="13", s="9", e="10"):
    return [menu, m, d, s, e]


# Reusable checks
BOOKED = dict(must=[BOOK, "JO18.330"], must_not=[MON, DAY, HR, ORDER])  # booked and room listed as open
NOTINT = dict(must=[M_NOTINT], must_not=["0 - 6"])                      # clear message, not the menu range text
AGENDA_DAY = dict(must=["No Meetings booked on this date."])
AGENDA_MONTH = dict(must=["No Meetings booked for this month."])

# ---------------- Equivalence partitioning ----------------
EP = [
    ("EP-01", ["0"], dict(must=["Exiting"])),
    ("EP-02", ["-1"], dict(must=[M_RANGE])),
    ("EP-03", ["7"], dict(must=[M_RANGE])),
    ("EP-04", ["abc"], dict(must=["Please enter a valid number from 0 - 6"])),
    ("EP-05", meet(), BOOKED),
    ("EP-06", meet_time(m="0"), dict(must=[MON])),
    ("EP-07", meet_time(m="13"), dict(must=[MON])),
    ("EP-08", ["6", "abc"], NOTINT),
    ("EP-09", meet_time(d="0"), dict(must=[DAY])),
    ("EP-10", meet_time(d="32"), dict(must=[DAY])),
    ("EP-11", meet_time(m="4", d="31"), dict(must=[DAY])),
    ("EP-12", ["6", "8", "abc"], NOTINT),
    ("EP-13", meet_time(s="-1"), dict(must=[HR])),
    ("EP-14", meet_time(s="24"), dict(must=[HR])),
    ("EP-15", ["6", "8", "13", "abc"], NOTINT),
    ("EP-16", meet_time(e="-1"), dict(must=[HR])),
    ("EP-17", meet_time(e="24"), dict(must=[HR])),
    ("EP-18", ["6", "8", "13", "9", "abc"], NOTINT),
    ("EP-19", meet_time(s="10", e="9"), dict(must=[ORDER])),
    ("EP-20", ["6", "8", "13", "9", "10", "XX9.999", "cancel"], dict(must=[ROOM])),
    ("EP-21", meet(people=("John Doe",)), dict(must=[EMP])),
    ("EP-22", ["6", "8", "13", "9", "10", "jo18.330", "cancel"], dict(must=[BOOK])),
    ("EP-23", meet(people=("justin gardener",)), dict(must=[BOOK], must_not=[EMP])),
    ("EP-24", meet(desc=""), dict(must=[BOOK])),
    ("EP-25", vac(), dict(must=[VAC])),
    ("EP-26", vac(sm="13"), dict(must=[MON])),
    ("EP-27", vac(sd="32"), dict(must=[DAY])),
    ("EP-28", vac(em="13"), dict(must=[MON])),
    ("EP-29", vac(ed="32"), dict(must=[DAY])),
    ("EP-30", vac(sd="20", ed="13"), dict(must_not=[VAC])),
    ("EP-31", ["5", "John Doe"], dict(must=[EMP])),
    ("EP-32", avail("4"), dict(must=["JO18.330"])),
    ("EP-33", avail("3"), dict(must=["Justin Gardener"])),
    ("EP-34", ["1", "Justin Gardener", "8", "13"], AGENDA_DAY),
    ("EP-35", ["1", "Justin Gardener", "8", "all"], AGENDA_MONTH),
    ("EP-36", ["1", "Justin Gardener", "8", "ALL"], AGENDA_MONTH),
    ("EP-37", ["1", "John Doe"], dict(must=[EMP])),
    ("EP-38", ["2", "JO18.330", "8", "13"], AGENDA_DAY),
    ("EP-39", ["2", "JO18.330", "8", "all"], AGENDA_MONTH),
    ("EP-40", ["2", "JO18.330", "8", "abc"], NOTINT),
    ("EP-41", ["2", "XX9.999"], dict(must=[ROOM])),
]


@pytest.mark.parametrize("inputs, expect", [pytest.param(i, e, id=n) for n, i, e in EP])
def test_equivalence_partitioning(monkeypatch, capsys, inputs, expect):
    check(monkeypatch, capsys, inputs, **expect)


# ---------------- Boundary value analysis ----------------
ERR_MON, ERR_DAY, ERR_HR = dict(must=[MON]), dict(must=[DAY]), dict(must=[HR])
BVA = [
    # menu
    ("BVA-01", ["-1"], dict(must=[M_RANGE])),
    ("BVA-02", ["0"], dict(must=["Exiting"])),
    ("BVA-03", ["1", "Justin Gardener", "8", "13"], AGENDA_DAY),
    ("BVA-04", vac(), dict(must=[VAC])),
    ("BVA-05", meet(), BOOKED),
    ("BVA-06", ["7"], dict(must=[M_RANGE])),
    # month
    ("BVA-07", meet_time(m="0"), ERR_MON),
    ("BVA-08", meet(m="1"), BOOKED),
    ("BVA-09", meet(m="2"), BOOKED),
    ("BVA-10", meet(m="11"), BOOKED),
    ("BVA-11", meet(m="12"), BOOKED),
    ("BVA-12", meet_time(m="13"), ERR_MON),
    # day (August)
    ("BVA-13", meet_time(d="0"), ERR_DAY),
    ("BVA-14", meet(d="1"), BOOKED),
    ("BVA-15", meet(d="2"), BOOKED),
    ("BVA-16", meet(d="30"), BOOKED),
    ("BVA-17", meet(d="31"), BOOKED),
    ("BVA-18", meet_time(d="32"), ERR_DAY),
    # February and November
    ("BVA-19", meet(m="2", d="28"), BOOKED),
    ("BVA-20", meet(m="2", d="29"), BOOKED),
    ("BVA-21", meet(m="2", d="30"), dict(must=[DAY])),
    ("BVA-22", meet(m="11", d="29"), BOOKED),
    ("BVA-23", meet(m="11", d="30"), BOOKED),
    ("BVA-24", meet(m="11", d="31"), dict(must=[DAY])),
    # start hour
    ("BVA-25", meet_time(s="-1", e="10"), ERR_HR),
    ("BVA-26", meet(s="0", e="1"), BOOKED),
    ("BVA-27", meet(s="1", e="2"), BOOKED),
    ("BVA-28", meet(s="22", e="23"), BOOKED),
    ("BVA-29", meet(s="23", e="23"), BOOKED),
    ("BVA-30", meet_time(s="24", e="23"), ERR_HR),
    # end hour
    ("BVA-31", meet_time(s="0", e="-1"), ERR_HR),
    ("BVA-32", meet(s="0", e="0"), BOOKED),
    ("BVA-33", meet(s="0", e="1"), BOOKED),
    ("BVA-34", meet(s="9", e="22"), BOOKED),
    ("BVA-35", meet(s="9", e="23"), BOOKED),
    ("BVA-36", meet_time(s="9", e="24"), ERR_HR),
    ("BVA-37", meet_time(s="10", e="9"), dict(must=[ORDER])),
    # vacation
    ("BVA-38", vac(sd="0", ed="20"), dict(must=[DAY])),
    ("BVA-39", vac(sd="1", ed="5"), dict(must=[VAC])),
    ("BVA-40", vac(sd="31", em="9", ed="5"), dict(must=[VAC])),
    ("BVA-41", vac(sd="32", em="9", ed="5"), dict(must=[DAY])),
    ("BVA-42", vac(sm="0"), dict(must=[MON])),
    ("BVA-43", vac(sm="1", sd="5", em="1", ed="10"), dict(must=[VAC])),
    ("BVA-44", vac(sm="12", sd="13", em="12", ed="31"), dict(must=[VAC])),
    ("BVA-45", vac(sm="13"), dict(must=[MON])),
    ("BVA-46", vac(em="13"), dict(must=[MON])),
    ("BVA-47", vac(ed="32"), dict(must=[DAY])),
    ("BVA-48", vac(sd="13", ed="12"), dict(must_not=[VAC])),
    ("BVA-49", vac(sd="13", ed="13"), dict(must=[VAC])),
    ("BVA-50", vac(sd="13", ed="14"), dict(must=[VAC])),
]


@pytest.mark.parametrize("inputs, expect", [pytest.param(i, e, id=n) for n, i, e in BVA])
def test_boundary_values(monkeypatch, capsys, inputs, expect):
    check(monkeypatch, capsys, inputs, **expect)
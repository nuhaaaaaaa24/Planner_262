import itertools

import pytest

from frontend.Planner import Planner

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


BOOKED = dict(must=[BOOK, "JO18.330"], must_not=[MON, DAY, HR, ORDER])
NOTINT = dict(must=[M_NOTINT], must_not=["0 - 6"])
AGENDA_DAY = dict(must=["No Meetings booked on this date."])
AGENDA_MONTH = dict(must=["No Meetings booked for this month."])

EP = [
    ("EP-01", ["-5"], dict(must=[M_RANGE])),
    ("EP-02", ["12"], dict(must=[M_RANGE])),
    ("EP-03", ["abc"], dict(must=["Please enter a valid number from 0 - 6"])),
    ("EP-04", [""], dict(must=["Please enter a valid number from 0 - 6"])),
    ("EP-05", ["1.5"], dict(must=["Please enter a valid number from 0 - 6"])),
    ("EP-06", meet(), BOOKED),
    ("EP-07", meet_time(m="-5"), dict(must=[MON])),
    ("EP-08", meet_time(m="20"), dict(must=[MON])),
    ("EP-09", ["6", "abc"], NOTINT),
    ("EP-10", meet_time(d="-5"), dict(must=[DAY])),
    ("EP-11", meet_time(d="45"), dict(must=[DAY])),
    ("EP-12", ["6", "8", "abc"], NOTINT),
    ("EP-13", meet_time(s="-5"), dict(must=[HR])),
    ("EP-14", meet_time(s="40"), dict(must=[HR])),
    ("EP-15", ["6", "8", "13", "abc"], NOTINT),
    ("EP-16", meet_time(e="-5"), dict(must=[HR])),
    ("EP-17", meet_time(e="40"), dict(must=[HR])),
    ("EP-18", ["6", "8", "13", "9", "abc"], NOTINT),
    ("EP-19", meet_time(s="15", e="4"), dict(must=[ORDER])),
    ("EP-20", ["6", "8", "13", "9", "10", "XX9.999", "cancel"], dict(must=[ROOM])),
    ("EP-21", meet(people=("John Doe",)), dict(must=[EMP])),
    ("EP-22", ["6", "8", "13", "9", "10", "jo18.330", "cancel"], dict(must=[BOOK])),
    ("EP-23", meet(people=("justin gardener",)), dict(must=[BOOK], must_not=[EMP])),
    ("EP-24", meet(desc=""), dict(must=[BOOK])),
    ("EP-25", vac(), dict(must=[VAC])),
    ("EP-26", vac(sm="20"), dict(must=[MON])),
    ("EP-27", vac(sd="45"), dict(must=[DAY])),
    ("EP-28", vac(em="20"), dict(must=[MON])),
    ("EP-29", vac(ed="45"), dict(must=[DAY])),
    ("EP-30", vac(sd="25", ed="5"), dict(must_not=[VAC])),
    ("EP-31", ["5", "John Doe"], dict(must=[EMP])),
    ("EP-32", vac(sm="-5"), dict(must=[MON])), #add to test case table
    ("EP-33", vac(sd="-5"), dict(must=[DAY])), #add to test case table
    ("EP-34", vac(em="-5"), dict(must=[MON])), #add to test case table
    ("EP-35", vac(ed="-5"), dict(must=[DAY])), #add to test case table
    ("EP-36", ["5", "Mike Smith", "abc"], NOTINT), #add to test case table
    ("EP-37", avail("4"), dict(must=["JO18.330"])),
    ("EP-38", avail("3"), dict(must=["Justin Gardener"])),
    ("EP-39", avail("4", m="20"), dict(must=[MON])),
    ("EP-40", avail("4", d="45"), dict(must=[DAY])),
    ("EP-41", avail("4", s="40"), dict(must=[HR])),
    ("EP-42", avail("4", s="15", e="4"), dict(must=[ORDER])),
    ("EP-43", meet() + avail("4"), dict(after_must_not=["JO18.330"])),
    ("EP-44", avail("3", m="20"), dict(must=[MON])),
    ("EP-45", meet() + avail("3"), dict(after_must_not=["Justin Gardener"])),
    ("EP-46", ["1", "Justin Gardener", "8", "13"], AGENDA_DAY),
    ("EP-47", ["1", "Justin Gardener", "8", "all"], AGENDA_MONTH),
    ("EP-48", ["1", "John Doe"], dict(must=[EMP])),
    ("EP-49", ["2", "JO18.330", "8", "13"], AGENDA_DAY),
    ("EP-50", ["2", "JO18.330", "8", "all"], AGENDA_MONTH),
    ("EP-51", ["2", "JO18.330", "8", "abc"], dict(must=[M_NOTINT])),
    ("EP-52", ["2", "XX9.999"], dict(must=[ROOM])),
    ("EP-53", meet() + ["1", "Justin Gardener", "8", "13"],
     dict(after_must=["Project review"],
          after_must_not=["No Meetings booked on this date."])),
    ("EP-54", meet() + ["2", "JO18.330", "8", "13"],
     dict(after_must=["Project review"],
          after_must_not=["No Meetings booked on this date."])),
    ("EP-55", ["1", "Justin Gardener", "20"], dict(must=[MON])),
    ("EP-56", ["2", "JO18.330", "8", "45"], dict(must=[DAY])),
]


@pytest.mark.parametrize("inputs, expect", [pytest.param(i, e, id=n) for n, i, e in EP])
def test_equivalence_partitioning(monkeypatch, capsys, inputs, expect):
    check(monkeypatch, capsys, inputs, **expect)


ERR_MON, ERR_DAY, ERR_HR = dict(must=[MON]), dict(must=[DAY]), dict(must=[HR])

BVA = [
    ("BVA-01", ["-1"], dict(must=[M_RANGE])),
    ("BVA-02", ["0"], dict(must=["Exiting"])),
    ("BVA-03", ["1", "Justin Gardener", "1", "1"], AGENDA_DAY),
    ("BVA-04", vac(sm="1", sd="1", em="1", ed="2"), dict(must=[VAC])),
    ("BVA-05", meet(m="3", d="4", s="11", e="12"), BOOKED),
    ("BVA-06", ["7"], dict(must=[M_RANGE])),
    ("BVA-07", meet_time(m="0"), ERR_MON),
    ("BVA-08", meet(m="1"), BOOKED),
    ("BVA-09", meet(m="2"), BOOKED),
    ("BVA-10", meet(m="11"), BOOKED),
    ("BVA-11", meet(m="12"), BOOKED),
    ("BVA-12", meet_time(m="13"), ERR_MON),
    ("BVA-13", meet_time(d="0"), ERR_DAY),
    ("BVA-14", meet(d="1"), BOOKED),
    ("BVA-15", meet(d="2"), BOOKED),
    ("BVA-16", meet(d="30"), BOOKED),
    ("BVA-17", meet(d="31"), BOOKED),
    ("BVA-18", meet_time(d="32"), ERR_DAY),
    ("BVA-19", meet(m="2", d="28"), BOOKED),
    ("BVA-20", meet(m="2", d="29"), BOOKED),
    ("BVA-21", meet(m="2", d="30"), ERR_DAY),
    ("BVA-22", meet(m="11", d="29"), BOOKED),
    ("BVA-23", meet(m="11", d="30"), BOOKED),
    ("BVA-24", meet(m="11", d="31"), ERR_DAY),
    ("BVA-25", meet_time(s="-1", e="10"), ERR_HR),
    ("BVA-26", meet(s="0", e="1"), BOOKED),
    ("BVA-27", meet(s="1", e="2"), BOOKED),
    ("BVA-28", meet(s="22", e="23"), BOOKED),
    ("BVA-29", meet(s="23", e="23"), BOOKED),
    ("BVA-30", meet_time(s="24", e="23"), ERR_HR),
    ("BVA-31", meet_time(s="0", e="-1"), ERR_HR),
    ("BVA-32", meet(s="0", e="0"), BOOKED),
    ("BVA-33", meet(s="9", e="22"), BOOKED),
    ("BVA-34", meet(s="9", e="23"), BOOKED),
    ("BVA-35", meet_time(s="9", e="24"), ERR_HR),
    ("BVA-36", meet_time(s="10", e="9"), dict(must=[ORDER])),
    ("BVA-37", vac(sd="0", ed="20"), ERR_DAY),
    ("BVA-38", vac(sd="1", ed="5"), dict(must=[VAC])),
    ("BVA-39", vac(sd="31", em="9", ed="5"), dict(must=[VAC])),
    ("BVA-40", vac(sd="32", em="9", ed="5"), ERR_DAY),
    ("BVA-41", vac(sm="0"), ERR_MON),
    ("BVA-42", vac(sm="1", sd="5", em="1", ed="10"), dict(must=[VAC])),
    ("BVA-43", vac(sm="12", sd="13", em="12", ed="31"), dict(must=[VAC])),
    ("BVA-44", vac(sm="13"), ERR_MON),
    ("BVA-45", vac(em="13"), ERR_MON),
    ("BVA-46", vac(ed="32"), ERR_DAY),
    ("BVA-47", vac(sd="13", ed="12"), dict(must_not=[VAC])),
    ("BVA-48", vac(sd="13", ed="13"), dict(must=[VAC])),
    ("BVA-49", vac(sd="13", ed="14"), dict(must=[VAC])),
    ("BVA-50", vac(em="0"), ERR_MON),
    ("BVA-51", vac(ed="0"), ERR_DAY),
    ("BVA-52", vac(sd="13", ed="31"), dict(must=[VAC])),
    ("BVA-53", vac(em="12"), dict(must=[VAC])),
    ("BVA-54", avail("4", m="12"), dict(must=["JO18.330"])),
    ("BVA-55", avail("4", d="31"), dict(must=["JO18.330"])),
    ("BVA-56", avail("4", m="2", d="29"), dict(must=["JO18.330"])),
    ("BVA-57", avail("4", m="11", d="30"), dict(must=["JO18.330"])),
    ("BVA-58", avail("4", s="23", e="23"), dict(must=["JO18.330"])),
    ("BVA-59", avail("4", m="0"), ERR_MON),
    ("BVA-60", avail("4", m="13"), ERR_MON),
    ("BVA-61", avail("4", d="32"), ERR_DAY),
    ("BVA-62", avail("4", s="24", e="23"), ERR_HR),
    ("BVA-63", avail("4", s="9", e="24"), ERR_HR),
]


@pytest.mark.parametrize("inputs, expect", [pytest.param(i, e, id=n) for n, i, e in BVA])
def test_boundary_values(monkeypatch, capsys, inputs, expect):
    check(monkeypatch, capsys, inputs, **expect)


ROOM2 = "JO18.331"


def check(monkeypatch, capsys, inputs, must=(), must_not=(), counts=(),
          after_must=(), after_must_not=()):
    """
    must / must_not          : text that must / must not appear anywhere in the output
    counts                   : (text, n) pairs, text must appear exactly n times
    after_must / after_must_not : same, but only for the output printed AFTER the first
                               'Meeting is now booked!' (used for tests that book, then look up)
    """
    out = run(monkeypatch, capsys, inputs)
    for text in must:
        assert text in out, f"Expected {text!r} in output:\n{out}"
    for text in must_not:
        assert text not in out, f"Did not expect {text!r} in output:\n{out}"
    for text, n in counts:
        assert out.count(text) == n, f"Expected {text!r} exactly {n} time(s), got {out.count(text)}:\n{out}"
    if after_must or after_must_not:
        assert BOOK in out, f"Setup booking did not succeed:\n{out}"
        tail = out.split(BOOK, 1)[1]
        for text in after_must:
            assert text in tail, f"Expected {text!r} after the booking:\n{tail}"
        for text in after_must_not:
            assert text not in tail, f"Did not expect {text!r} after the booking:\n{tail}"


CF = [
    ("CF-01", meet() + meet(people=("Mike Smith",)), dict(counts=[(BOOK, 1)])),
    ("CF-02", meet() + meet(room=ROOM2), dict(counts=[(BOOK, 1)])),
    ("CF-03", meet(s="9", e="11") + meet(s="10", e="12", people=("Mike Smith",)),
     dict(counts=[(BOOK, 1)])),
    ("CF-04", meet(s="9", e="10") + meet(s="10", e="11", people=("Mike Smith",)),
     dict(counts=[(BOOK, 2)])),
    ("CF-05", meet(s="9", e="10") + meet(s="8", e="12", people=("Mike Smith",)), 
     dict(counts=[(BOOK, 1)])),
]


@pytest.mark.parametrize("inputs, expect", [pytest.param(i, e, id=n) for n, i, e in CF])
def test_booking_conflicts(monkeypatch, capsys, inputs, expect):
    check(monkeypatch, capsys, inputs, **expect)
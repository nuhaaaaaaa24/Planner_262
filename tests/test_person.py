"""
This file contains test cases for the Person class.

According to the CFG, there are two branches in this
class (print_agenda, add_meeting)

Many of these tests resemble those of the Room class.
"""

# import the required classes from logic
import pytest
from unittest.mock import MagicMock

from logic.Person import Person
from logic.Room import Room
from logic.Calendar import Calendar
from logic.Meeting import Meeting
from logic.ConflictException import ConflictsException

# Fixture to create an instance of person for the tests
@pytest.fixture
def person():
    return Person("Alice") # we only test one person right now

def meeting(month=5, day=10, start=3, end=5, desc="m", **kw):
    return Meeting(month, day, start, end, description=desc, **kw)

# -------------- Section 1: Initialize, get ID --------------

class PersonInitialize:
    # UT23: Test that the ID is empty by default.
    # Expected behaviour: Return empty string
    def test_default_id(self):
        assert Person().get_id() == ""

    # UT24: Test that each person has their own Calendar() instance.
    # Expected behaviour: Each person builds a separate Calendar() instance.
    def test_person_owns_calendar(self):
        persA = Person("A")
        persB = Person("B")

        assert isinstance(persA.calendar, Calendar)
        assert persA.calendar is not persB.calendar

        persA.add_meeting(meeting())
        assert persB.is_busy(11, 5, 7, 9) is False

# -------------- Section 2: Add meetings --------------
class TestMeetings:

    # UT25: Test that the add_meeting try block completes successfully
    # Expected behaviour: Meeting is added successfully
    def test_add_meeting_pass(self, person):
        m = meeting()
        person.add_meeting(m)
        assert person.get_meeting(5, 10, 0) is m

    # UT26: Test except branch - meeting overlaps with another meeting
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_overlap(self, person):
        person.add_meeting(meeting(start=9, end=12, desc="meeting one"))
        with pytest.raises(ConflictsException) as exc:
            person.add_meeting(meeting(start=11, end=14, desc="meeting two"))
        text = str(exc.value)

        # also check that the error message is correct
        assert text.startswith("Conflict for attendee Alice:\n")

    # UT27: Test except branch - meeting starts at the end of last meeting
    # Expected behaviour: Meeting can be created
    def test_add_meeting_fail_no_overlap(self, person):
            m1 = person.add_meeting(meeting(start=9, end=12, desc="meeting one"))
            m2 = person.add_meeting(meeting(start=12, end=14, desc="meeting two"))

            person.add_meeting(m1)
            person.add_meeting(m2)

            assert person.get_meeting(5, 10, 0) is m1
            assert person.get_meeting(5, 10, 1) is m2

    # UT28: Test except branch - invalid months are checked
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_invalid_months(self, person):
        with pytest.raises(ConflictsException):
            person.add_meeting(meeting(month=16))

    # UT29: Test except branch - invalid days are checked
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_invalid_days(self, person):
        with pytest.raises(ConflictsException):
            person.add_meeting(meeting(day=32))

    # UT30: Test except branch - invalid times are checked
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_invalid_times(self, person):
        with pytest.raises(ConflictsException):
            person.add_meeting(meeting(start=25))

    # UT31: Test except branch - failure leaves calendar unchanged
    # Expected behaviour: Calendar returns one index value for the date May 10
    def test_add_meeting_fail_check_calendar(self, person):
        person.add_meeting(meeting())
        with pytest.raises(ConflictsException):
            person.add_meeting(meeting(start=4, end=5))
        assert len(person.calendar.occupied[5][10]) == 1

    # UT32: Check that only ConflictsException is triggered
    # Expected behaviour: Try-except block completes even if a RuntimeError is thrown
    def test_only_conflictsexception(self, person):
        person.calendar = MagicMock()
        person.calendar.add_meeting.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            person.add_meeting(meeting())

class TestPersonPrintAgenda:

    # UT33: For "day is None == False" branch, check that agenda prints meeting correctly
    # Expected behaviour: Agenda prints with meeting
    def test_agenda_day_meeting_exists(self, person):
        person.add_meeting(meeting(desc="Dummy meeting for day is None = False branch"))
        agenda = person.print_agenda(5, 10)
        assert agenda.startswith("Agenda for 5/10 are as follows:\n") # check that the correct message is sent
        assert "Dummy meeting for day is None = False branch" in agenda

    # UT34: For "day is None == False" branch, check that agenda does not print invalid meeting
    # Expected behaviour: Agenda prints without invalid meeting
    def test_agenda_day_true_no_invalid_meeting(self, person):
        person.add_meeting(meeting(desc="Dummy meeting for day is None = False branch"))
        with pytest.raises(ConflictsException):
            person.add_meeting(meeting(start=25, desc="Invalid meeting for day is None = False branch"))
        agenda = person.print_agenda(5, 10)
        assert "Invalid meeting for day is None = False branch" not in agenda

    # UT35: For "day is None == False" branch, check that agenda prints without a meeting correctly
    # Expected behaviour: Agenda prints without meeting
    def test_agenda_day_no_meeting(self, person):
        assert person.print_agenda(5, 10) == "No Meetings booked on this date.\n\n"

    # UT36: For "day is None == True" branch, check that agenda is printed for the month
    # Expected behaviour: Returns the agenda for the month
    def test_agenda_no_day_prints_month(self, person):
        person.calendar = MagicMock()
        person.calendar.print_agenda.return_value = "MONTH"
        assert person.print_agenda(5) == "MONTH"
        person.calendar.print_agenda.assert_called_once_with(5) # check that only month was passed to the calendar

    # UT37: Check that "day == all" returns the agenda for the month
    # Expected behaviour: Return monthly calendar
    def test_agenda_all_days(self, person):
        person.add_meeting(meeting(month=3, day=4, desc="Meeting to check agenda=all option"))
        assert "Meeting to check agenda=all option" in person.print_agenda(month=3, day="all")

# -------------- Section 4: is busy --------------

class TestPersonIsBusy:
    # UT38: Test that an unoccupied person is not busy, then re-check after adding a meeting
    # Expected behaviour: is_busy initally False, then set to True afterwards
    def test_is_busy_false_then_true(self, person):
        assert person.is_busy(5, 10, 9, 11) is False
        person.add_meeting(meeting(5, 10, 9, 9))  # note: overlapping start/end time goes through
        assert person.is_busy(5, 10, 9, 11) is True

    # UT39: Test that invalid input is not accepted
    # Expected behaviour: Raises ConflictException
    def test_is_busy_invalid_input(self, person):
        with pytest.raises(ConflictsException):
            person.is_busy(5, 35, 9, 10)

# -------------- Section 5: get meeting --------------

class TestPersonGetMeeting:
    # UT40: Check that get_meeting completes successfully
    # Expected outcome: Return valid meeting
    def test_get_meeting_pass(self, person):
        m = meeting()
        person.add_meeting(m)
        assert person.get_meeting(5, 10, 0) is m

    # UT41: Check that non-existent meetings are not returned
    # Expected behaviour: Raises IndexError 
    def test_get_meeting_fail(self, person):
        with pytest.raises(IndexError):
            person.get_meeting(5, 10, 0)

# -------------- Section 5: remove meeting --------------
class TestPersonRemoveMeeting:
    # UT42: Check that remove_meeting completes successfully
    # Expected outcome: remove_meeting completes successfully
    def test_remove_meeting_pass(self, person):
        m = meeting()
        person.add_meeting(m)
        person.remove_meeting(5, 10, 0)
        assert person.is_busy(5, 10, 9, 11) is False

    # UT43: Check that invalid meetings throw errors
    # Expected outcome: Raises IndexError
    def test_remove_meeting_fail(self, person):
        with pytest.raises(IndexError):
            person.remove_meeting(5, 10, 0)

# -------------- Section 6: Miscellaneous tests --------------

class TestPersonMisc:
    # UT44: Check that person passes its args to Calendar correctly
    # Expected outcome: Args are passed with no changes
    def test_person_passes_args(self, person):
        person.calendar = MagicMock()
        person.is_busy(1, 2, 3, 4)
        person.get_meeting(1, 2, 0)
        person.remove_meeting(1, 2, 0)

        person.calendar.is_busy.assert_called_once_with(1, 2, 3, 4)
        person.calendar.get_meeting.assert_called_once_with(1, 2, 0)
        person.calendar.remove_meeting.assert_called_once_with(1, 2, 0)

    # UT45: Test that many people can attend one meeting 
    # Expected behaviour: one meeting object appears in many people's calendars
    def test_many_people_one_meeting(self):
        a = Person("Alice")
        b = Person("Bob")
        r1 = Room("Room1")
        m = Meeting(6, 3, 9, 10, [a, b], r1, "Testing multi-person meetings")

        for owner in (a, b, r1):
            owner.add_meeting(m)

        meet_a = a.get_meeting(6, 3, 0)
        meet_b = b.get_meeting(6, 3, 0)
        meet_r1 = r1.get_meeting(6, 3, 0)

        assert meet_a is meet_b is meet_r1

    # UT46: Test that a busy attendee is blocked from joining a meeting, 
    #       but a free attendee is not
    # Expected behaviour: Busy attendee not allowed to join, free attendee allowed
    def test_busy_attendee_blocked_free_attendee_allowed(self):
        a = Person("Alice")
        b = Person("Bob")
        a.add_meeting(meeting(start=3, end=5))
        m = b.add_meeting(meeting(start=4, end=9))

        with pytest.raises(ConflictsException):
            a.add_meeting(meeting(start=4, end=9))

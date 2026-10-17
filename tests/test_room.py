"""
This file contains test cases for the Room class.

According to the CFG, there are two branches in this
class (print_agenda, add_meeting)
"""

# import the required classes from logic
import pytest
from unittest.mock import MagicMock

from logic.Room import Room 
from logic.Calendar import Calendar
from logic.Meeting import Meeting
from logic.ConflictException import ConflictsException

# Fixture to create an instance of Room for the tests
@pytest.fixture
def room():
    return Room("JOI.230") # we only test one room right now

# helper to create a meeting
def meeting(month=5, day=10, start=9, end=11, desc="m"):
    return(Meeting(month, day, start, end, description=desc))

# -------------- Section 1: Initialize, get ID --------------
class TestInitialization:

    # UT01: Test that the ID is empty by default.
    # Expected behaviour: Return empty string
    def test_default_id(self):
        assert Room().get_id() == ""

    # UT02: Test that each room has its own Calendar() instance.
    # Expected behaviour: Each room builds a separate Calendar() instance.
    def test_room_owns_calendar(self):
        roomA = Room("A")
        roomB = Room("B")

        assert isinstance(roomA.calendar, Calendar)
        assert roomA.calendar is not roomB.calendar

        roomA.add_meeting(meeting())
        assert roomB.is_busy(12, 5, 7, 9) is False

# -------------- Section 2: Add meetings --------------
class TestMeetings:

    # UT03: Test that the add_meeting try block completes successfully
    # Expected behaviour: Meeting is added successfully
    def test_add_meeting_pass(self, room):
        m = meeting()
        room.add_meeting(m)
        assert room.get_meeting(5, 10, 0) is m

    # UT04: Test except branch - meeting overlaps with another meeting
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_overlap(self, room):
        room.add_meeting(meeting(start=9, end=12, desc="meeting one"))
        with pytest.raises(ConflictsException) as exc:
            room.add_meeting(meeting(start=11, end=14, desc="meeting two"))
        text = str(exc.value)

        # also check that the error message is correct
        assert text.startswith("Conflict for room JOI.230:\n")

    # UT05: Test except branch - meeting starts at the end of last meeting
    # Expected behaviour: Meeting can be created
    def test_add_meeting_fail_no_overlap(self, room):
            m1 = room.add_meeting(meeting(start=9, end=12, desc="meeting one"))
            m2 = room.add_meeting(meeting(start=12, end=14, desc="meeting two"))

            room.add_meeting(m1)
            room.add_meeting(m2)

            assert room.get_meeting(5, 10, 0) is m1
            assert room.get_meeting(5, 10, 1) is m2

    # UT06: Test except branch - invalid months are checked
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_invalid_months(self, room):
        with pytest.raises(ConflictsException):
            room.add_meeting(meeting(month=16))

    # UT07: Test except branch - invalid days are checked
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_invalid_days(self, room):
        with pytest.raises(ConflictsException):
            room.add_meeting(meeting(day=32))

    # UT08: Test except branch - invalid times are checked
    # Expected behaviour: Raise ConflictsException
    def test_add_meeting_fail_invalid_times(self, room):
        with pytest.raises(ConflictsException):
            room.add_meeting(meeting(start=25))

    # UT09: Test except branch - failure leaves room unchanged
    # Expected behaviour: Calendar returns one index value for the date May 10
    def test_add_meeting_fail_check_room_state(self, room):
        room.add_meeting(meeting())
        with pytest.raises(ConflictsException):
            room.add_meeting(meeting(start=10, end=11))
        assert len(room.calendar.occupied[5][10]) == 1

    # UT10: Check that only ConflictsException is triggered
    # Expected behaviour: Try-except block completes even if a RuntimeError is thrown
    def test_only_conflictsexception(self, room):
        room.calendar = MagicMock()
        room.calendar.add_meeting.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="boom"):
            room.add_meeting(meeting())

# -------------- Section 3: Print agenda --------------

class TestRoomPrintAgenda:

    # UT11: For "day is None == False" branch, check that agenda prints meeting correctly
    # Expected behaviour: Agenda prints with meeting
    def test_agenda_day_meeting_exists(self, room):
        room.add_meeting(meeting(desc="Dummy meeting for day is None = False branch"))
        agenda = room.print_agenda(5, 10)
        assert agenda.startswith("Agenda for 5/10 are as follows:\n") # check that the correct message is sent
        assert "Dummy meeting for day is None = False branch" in agenda

    # UT12: For "day is None == False" branch, check that agenda does not print invalid meeting
    # Expected behaviour: Agenda prints without invalid meeting
    def test_agenda_day_true_no_invalid_meeting(self, room):
        room.add_meeting(meeting(desc="Dummy meeting for day is None = False branch"))
        with pytest.raises(ConflictsException):
            room.add_meeting(meeting(start=25, desc="Invalid meeting for day is None = False branch"))
        agenda = room.print_agenda(5, 10)
        assert "Invalid meeting for day is None = False branch" not in agenda

    # UT13: For "day is None == False" branch, check that agenda prints without a meeting correctly
    # Expected behaviour: Agenda prints without meeting
    def test_agenda_day_no_meeting(self, room):
        assert room.print_agenda(5, 10) == "No Meetings booked on this date.\n\n"

    # UT14: For "day is None == True" branch, check that agenda is printed for the month
    # Expected behaviour: Returns the agenda for the month
    def test_agenda_no_day_prints_month(self, room):
        room.calendar = MagicMock()
        room.calendar.print_agenda.return_value = "MONTH"
        assert room.print_agenda(5) == "MONTH"
        room.calendar.print_agenda.assert_called_once_with(5) # check that only month was passed to the calendar

    # UT15: Check that "day == all" returns the agenda for the month
    # Expected behaviour: Return monthly calendar
    def test_agenda_all_days(self, room):
        room.add_meeting(meeting(month=3, day=4, desc="Meeting to check agenda=all option"))
        assert "Meeting to check agenda=all option" in room.print_agenda(month=3, day="all")

# -------------- Section 4: is busy --------------

class TestRoomIsBusy:
    # UT16: Test that an unoccupied room is not busy, then re-check after adding a meeting
    # Expected behaviour: is_busy initally False, then set to True afterwards
    def test_is_busy_false_then_true(self, room):
        assert room.is_busy(5, 10, 9, 11) is False
        room.add_meeting(meeting(5, 10, 9, 9))  # note: overlapping start/end time goes through
        assert room.is_busy(5, 10, 9, 11) is True

    # UT17: Test that invalid input is not accepted
    # Expected behaviour: Raises ConflictException
    def test_is_busy_invalid_input(self, room):
        with pytest.raises(ConflictsException):
            room.is_busy(5, 31, 9, 10)

# -------------- Section 5: get meeting --------------

class TestRoomGetMeeting:
    # UT18: Check that get_meeting completes successfully
    # Expected outcome: Return valid meeting
    def test_get_meeting_pass(self, room):
        m = meeting()
        room.add_meeting(m)
        assert room.get_meeting(5, 10, 0) is m

    # UT19: Check that non-existent meetings are not returned
    # Expected behaviour: Raises IndexError 
    def test_get_meeting_fail(self, room):
        with pytest.raises(IndexError):
            room.get_meeting(5, 10, 0)

# -------------- Section 5: remove meeting --------------
class TestRoomRemoveMeeting:
    # UT20: Check that remove_meeting completes successfully
    # Expected outcome: remove_meeting completes successfully
    def test_remove_meeting_pass(self, room):
        m = meeting()
        room.add_meeting(m)
        room.remove_meeting(5, 10, 0)
        assert room.is_busy(5, 10, 9, 11) is False

    # UT21: Check that invalid meetings throw errors
    # Expected outcome: Raises IndexError
    def test_remove_meeting_fail(self, room):
        with pytest.raises(IndexError):
            room.remove_meeting(5, 10, 0)

# -------------- Section 6: Miscellaneous tests --------------
class TestRoomMisc:
    # UT22: Check that Room passes its args to Calendar correctly
    # Expected outcome: Args are passed with no changes
    def test_room_passes_args(self, room):
        room.calendar = MagicMock()
        room.is_busy(1, 2, 3, 4)
        room.get_meeting(1, 2, 0)
        room.remove_meeting(1, 2, 0)

        room.calendar.is_busy.assert_called_once_with(1, 2, 3, 4)
        room.calendar.get_meeting.assert_called_once_with(1, 2, 0)
        room.calendar.remove_meeting.assert_called_once_with(1, 2, 0)

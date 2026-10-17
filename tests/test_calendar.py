"""
This file contains the structural tests pertaining to the Calendar class. 

Note that some tests use xfail to work around defects in the code. For example,
the Calendar class defines print_agenda twice, meaning the latter function
overrides the former. This interferes with defect D9; see the report for more details.
"""

# import the required classes from logic
import pytest
from unittest.mock import MagicMock

from logic.Room import Room 
from logic.Calendar import Calendar
from logic.Meeting import Meeting
from logic.ConflictException import ConflictsException
from logic.Person import Person

@pytest.fixture
def calendar():
    return Calendar()

def meeting(month=5, day=10, start=9, end=11, desc="m", **kw):
    return Meeting(month, day, start, end, description=desc, **kw)

# -------------- Section 1: Initialize, get ID --------------

class TestCalendarInit:

    # UT-48: Test that all months and days can be used
    # Expected outcome: Months with values from 1-12 and days
    #                   with values from 1-31 (with some exceptions)
    #                   can be used to plan meetings
    def test_months_and_days(self, calendar):
        assert sorted(calendar.occupied) == list(range(0, 13)) # 13 is excluded from the list
        for month in calendar.occupied:
            assert sorted(calendar.occupied[month]) == list(range(0, 32))

    # UT-49: Test that days in the calendar are empty by default.
    # Expected outcome: Return empty lists
    def test_normal_days_start_empty(self, calendar):
        assert calendar.occupied[5][10] == []
        assert calendar.occupied[1][1] == []

# -------------- Section 2: check times --------------

class TestCheckTimes:

    # UT-50: Test that checks several values to see if they are accepted
    # Expected outcome: All values pass successfully
    @pytest.mark.parametrize("m, d, s, e", [(1, 1, 0, 0), (11, 30, 22, 23), (6, 15, 9, 17), (6, 15, 10, 10)])
    def test_semirandom_valid_values(self, m, d, s, e):
        assert Calendar.check_times(m, d, s, e) is None

    # UT51: Test that checks if invalid dates below 0 are allowed
    # Expected outcome: Return ConflictsException
    @pytest.mark.parametrize("day", [0, -1])
    def test_day_too_small(self, day):
        with pytest.raises(ConflictsException, match="Day does not exist"):
            Calendar.check_times(5, day, 9, 10)

    # UT52: Test that checks if invalid dates above 31 are allowed
    # Expected outcome: Return ConflictsException
    @pytest.mark.parametrize("day", [31, 100])
    def test_day_too_large(self, day):
        with pytest.raises(ConflictsException, match="Day does not exist"):
            Calendar.check_times(5, day, 9, 10)

    # UT53: Test that checks if invalid months below 0 are allowed
    # Expected outcome: Return ConflictsException
    @pytest.mark.parametrize("month", [0, -3])
    def test_month_too_small(self, month):
        with pytest.raises(ConflictsException, match="Month does not exist"):
            Calendar.check_times(month, 10, 9, 10)

    # UT54: Test that checks if invalid months above 12 are allowed
    # Expected outcome: Return ConflictsException
    @pytest.mark.parametrize("month", [12, 13])
    def test_month_too_large(self, month):
        with pytest.raises(ConflictsException, match="Month does not exist"):
            Calendar.check_times(month, 10, 9, 10)

    # UT55: Test that checks if invalid start times below 0 are allowed
    # Expected outcome: Return ConflictsException
    def test_start_negative(self):
        with pytest.raises(ConflictsException, match="Illegal hour"):
            Calendar.check_times(5, 10, -1, 10)

    # UT56: Test that checks if invalid start times above 24 are allowed
    # Expected outcome: Return ConflictsException
    @pytest.mark.parametrize("start", [23, 24])
    def test_start_too_large(self, start):
        with pytest.raises(ConflictsException, match="Illegal hour"):
            Calendar.check_times(5, 10, start, 23)

    # UT57: Test that checks if invalid end times below 0 are allowed
    # Expected outcome: Return ConflictsException
    def test_end_negative(self):
        with pytest.raises(ConflictsException, match="Illegal hour"):
            Calendar.check_times(5, 10, 0, -1)

    # UT58: Test that checks if invalid end times above 24 are allowed
    # Expected outcome: Return ConflictsException
    def test_end_too_large(self):
        with pytest.raises(ConflictsException, match="Illegal hour"):
            Calendar.check_times(5, 10, 0, 24)

    # UT59: Test that checks if meetings with start times after end times are allowed
    # Expected outcome: Return ConflictsException
    def test_start_after_end(self):
        with pytest.raises(ConflictsException, match="starts before it ends"):
            Calendar.check_times(5, 10, 12, 11)

    # ---- The below are identified defects. They have been marked with xfail to signify required changes. ----
    # UT60: Test for December as invalid month
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="December (index 12) fails despite being a valid month")
    def test_december_should_be_valid(self):
        Calendar.check_times(12, 10, 9, 10)

    # UT61: Test for day 31 as an invalid day
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="The 31st day of any given month is rejected despite being a valid date")
    def test_day_31_should_be_valid(self):
        Calendar.check_times(1, 31, 9, 10)

    # UT62: Test for hour 23 as an invalid hour
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="The 23rd hour is rejected despite being a valid hour")
    def test_start_23_should_be_valid(self):
        Calendar.check_times(1, 1, 23, 23)

# -------------- Section 3: add_meeting --------------

class TestAddMeeting:

    # UT63: Test whether meetings can be added to empty days
    # Expected outcome: Meetings can be added to empty days
    def test_add_to_empty_day(self, calendar):
        m = meeting()
        calendar.add_meeting(m)
        assert calendar.occupied[5][10] == [m]

    # UT64: Test whether invalid input is allowed
    # Expected outcome: Raise ConflictsException and return empty day 
    def test_invalid_input_propagates_from_check_times(self, calendar):
        with pytest.raises(ConflictsException, match="Month does not exist"):
            calendar.add_meeting(meeting(month=13))
        assert calendar.occupied[5][10] == []

    # UT65: Test if multiple non-overlapping meetings are allowed on the same day
    # Expected outcome: Non-overlapping meetings can be booked
    def test_non_overlapping_meetings_same_day(self, calendar):
        a = meeting(start=9, end=10)
        b = meeting(start=12, end=14)
        calendar.add_meeting(a)
        calendar.add_meeting(b)
        assert calendar.occupied[5][10] == [a, b]

    # UT66: Test that meetings on different days do not conflict due to similar times
    # Expected outcome: Meetings on different days with the same start/end times are allowed
    def test_meetings_on_different_days_do_not_conflict(self, calendar):
        calendar.add_meeting(meeting(day=10, start=9, end=11))
        calendar.add_meeting(meeting(day=11, start=9, end=11))
        assert len(calendar.occupied[5][10]) == 1 and len(calendar.occupied[5][11]) == 1

    # UT67: Test for overlapping meetings (start overlaps)
    # Expected outcome: Overlapping meetings are rejected
    def test_conflict_start_inside_existing(self, calendar):
        calendar.add_meeting(meeting(start=9, end=12, desc="Meeting one for overlap test"))
        with pytest.raises(ConflictsException) as exc:
            calendar.add_meeting(meeting(start=10, end=14, desc="Meeting two for overlap test"))

        assert "Overlap with another item - Meeting one for overlap test" in str(exc.value)
        assert len(calendar.occupied[5][10]) == 1 

    # UT68: Test for overlapping meetings (end overlaps)
    # Expected outcome: Overlapping meetings are rejected
    def test_conflict_end_inside_existing(self, calendar):
        calendar.add_meeting(meeting(start=10, end=12, desc="first meeting"))
        with pytest.raises(ConflictsException, match="Overlap"):
            calendar.add_meeting(meeting(start=8, end=11, desc="second meeting"))

    # UT69: Test for adjacent meetings
    # Expected outcome: Adjacent meetings are allowed
    def test_adjacent_but_not_touching_is_allowed(self, calendar):
        calendar.add_meeting(meeting(start=9, end=12))
        calendar.add_meeting(meeting(start=13, end=15))
        assert len(calendar.occupied[5][10]) == 2

    # UT70: Test for which error message is generated
    # Expected outcome: Last conflict is displayed
    # Note that this may not be intended behaviour if the client wishes to see all conflicts.
    def test_conflict_reports_last_conflicting_meeting(self, calendar):
        calendar.add_meeting(meeting(start=1, end=3, desc="A"))
        calendar.add_meeting(meeting(start=5, end=7, desc="B"))
        with pytest.raises(ConflictsException) as exc:
            calendar.add_meeting(meeting(start=2, end=6, desc="C"))  
        assert "- B -" in str(exc.value) # always generated in error messages

    # UT71: Test placeholder dates - Feb 30 is allowed
    # Expected outcome: Feb 30 is allowed
    # This is a defect.
    def test_placeholder_meetings_are_skipped_in_conflict_check(self, calendar):
        m = meeting(month=2, day=30, start=9, end=10)
        calendar.add_meeting(m)
        assert m in calendar.occupied[2][30]

    # UT72: Test if a meeting entered on a placeholder date (which contain placeholder meetings to prevent bookings)
    #       can be booked
    # Expected behaviour: Raise ConflictsException
    def test_meeting_checked_alongside_placeholder(self, calendar):
        calendar.add_meeting(meeting(month=11, day=30, start=9, end=11, desc="Test meeting"))
        with pytest.raises(ConflictsException, match="Test meeting"):
            calendar.add_meeting(meeting(month=11, day=30, start=10, end=12))

    # UT73: Test for missing months (TRUE branch of if m_month not in self_occupied)
    # Expected outcome: Missing months must exist or be re-created
    def test_missing_month_is_created(self, calendar):
        del calendar.occupied[5]
        m = meeting()
        calendar.add_meeting(m)
        assert calendar.occupied[5][10] == [m]

    # UT74: Test for missing days (TRUE branch of if m_month not in self_occupied[m_month])
    # Expected outcome: Missing days must exist or be re-created
    def test_missing_day_is_created(self, calendar):
        del calendar.occupied[5][10]
        m = meeting()
        calendar.add_meeting(m)
        assert calendar.occupied[5][10] == [m]

    # UT75: Test that meetings can be booked on non-existent days
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="Meetings can be booked on some non-existent dates (e.g. Feb 30)")
    def test_cannot_book_nonexistent_day(self, calendar):
        with pytest.raises(ConflictsException):
            calendar.add_meeting(meeting(month=2, day=30))

    # UT76: Test that fully overlapping meetings can be booked together
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="One meeting can fully overlap another.")
    def test_enclosing_meeting_should_conflict(self, calendar):
        calendar.add_meeting(meeting(start=10, end=11))
        with pytest.raises(ConflictsException):
            calendar.add_meeting(meeting(start=9, end=12))


# -------------- Section 4: is busy --------------

class TestCalendarIsBusy:

    # UT77: Test that empty days always return not busy
    # Expected outcome: is_busy returns False
    def test_empty_day_not_busy(self, calendar):
        assert calendar.is_busy(5, 10, 9, 10) is False

    # UT78: Test that invalid input is rejected
    # Expected outcome: Raise ConflictsException
    def test_invalid_input_raises(self, calendar):
        with pytest.raises(ConflictsException):
            calendar.is_busy(5, 35, 9, 10)

    # UT79: Test that is_busy returns True in a meeting
    # Expected outcome: is_busy returns True
    def test_busy_when_start_inside_meeting(self, calendar):
        calendar.add_meeting(meeting(start=9, end=12))
        assert calendar.is_busy(5, 10, 10, 14) is True

    # UT80: Test that is_busy returns true when the required time starts earlier 
    # than a meeting but ends inside one
    # Expected outcome: is_busy returns True
    def test_busy_when_end_inside_meeting(self, calendar):
        calendar.add_meeting(meeting(start=10, end=12))
        assert calendar.is_busy(5, 10, 8, 11) is True

    # UT81: Test that is_busy returns false when the required time and meeting times do not overlap
    # Expected outcome: is_busy returns false
    def test_not_busy_before_meeting(self, calendar):
        calendar.add_meeting(meeting(start=10, end=12))
        assert calendar.is_busy(5, 10, 6, 8) is False

    # UT82: Test that is_busy returns false when the meeting end time overlaps with the required time
    # Expected outcome: is_busy returns false
    def test_not_busy_after_meeting(self, calendar):
        calendar.add_meeting(meeting(start=10, end=12))
        assert calendar.is_busy(5, 10, 14, 16) is False

    # UT83: Test that is_busy returns true for overlapping boundaries
    # Expected outcome: is_busy returns true
    @pytest.mark.parametrize("start, end", [(12, 14), (8, 10)])
    def test_overlapping_boundaries_are_busy(self, calendar, start, end):
        calendar.add_meeting(meeting(start=10, end=12))
        assert calendar.is_busy(5, 10, start, end) is True

    # UT84: Test that is_busy only applies to the specified date
    # Expected outcome: is_busy returns false on a different date
    def test_busy_only_on_day(self, calendar):
        calendar.add_meeting(meeting(day=10, start=9, end=12))
        assert calendar.is_busy(5, 11, 9, 12) is False

    # UT85: Test that is_busy applies to multiple non-overlapping meetings
    # Expected outcome: is_busy returns true
    def test_busy_with_multiple_meetings(self, calendar):
        calendar.add_meeting(meeting(start=1, end=2))
        calendar.add_meeting(meeting(start=10, end=12))
        assert calendar.is_busy(5, 10, 11, 11) is True

    # UT86: Test that placeholder invalid dates always return is_busy
    # Expected outcome: February 30 returns true for is_busy
    def test_placeholder_day_reports_busy(self, calendar):
        assert calendar.is_busy(2, 30, 9, 10) is True

    # UT87: Test that queries for a time inside a meeting do not return is_busy
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="Queries inside an existing meeting time do not return is_busy")
    def test_query_inside_meeting_should_be_busy(self, calendar):
        calendar.add_meeting(meeting(start=10, end=11))
        assert calendar.is_busy(5, 10, 9, 12) is True


# -------------- Section 5: clear schedule --------------

class TestCalendarClear:

    # UT88: Test that clearing the schedule deletes meetings
    # Expected outcome: Date is cleared and is_busy is reset to false
    def test_clear_schedule_with_meetings_pass(self, calendar):
        calendar.add_meeting(meeting(start=1, end=2))
        calendar.add_meeting(meeting(start=5, end=6))
        calendar.clear_schedule(5, 10)
        assert calendar.occupied[5][10] == []
        assert calendar.is_busy(5, 10, 1, 6) is False

    # UT89: Test to clear the schedule on an empty day
    # Expected outcome: Schedule remains clear, no errors thrown
    def test_clear_schedule_on_empty_day(self, calendar):
        calendar.clear_schedule(5, 10)
        assert calendar.occupied[5][10] == []

    # UT90: Test that schedule clears only affect the selected date
    # Expected outcome: Schedule clear only applies to the selected date
    def test_clear_schedule_only_affects_selected_date(self, calendar):
        other = meeting(day=11)
        calendar.add_meeting(other)
        calendar.clear_schedule(5, 10)
        assert calendar.occupied[5][11] == [other]

# -------------- Section 5: print agenda --------------

class TestCalendarPrintAgenda:

    # UT91: Test that a non-empty schedule returns the correct agenda
    # Expected outcome: Agenda is correctly printed 
    def test_agenda_for_non_empty_day(self, calendar):
        a = Meeting(5, 10, 9, 10, [Person("Ann")], Room("R1"), "One")
        b = meeting(start=12, end=13, desc="Two")
        calendar.add_meeting(a)
        calendar.add_meeting(b)
        assert calendar.print_agenda(5, 10) == (
            "Agenda for 5/10 are as follows:\n" + str(a) + "\n"+ str(b) + "\n"
        )

    # UT92: Test that an empty schedule returns an empty agenda
    # Expected outcome: Agenda is empty
    def test_agenda_for_empty_day(self, calendar):
        assert calendar.print_agenda(5, 10) == "No Meetings booked on this date.\n\n"

    # UT93: Test that a missing month returns an empty agenda
    # Expected outcome: Agenda is empty
    # Note that the client may prefer to intercept incorrect month values such as
    # the one used for this test.
    def test_agenda_for_missing_month(self, calendar):
        assert calendar.print_agenda(99, 1) == "No Meetings booked on this date.\n\n"

    # UT94: Test that a missing month returns an empty agenda
    # Expected outcome: Agenda is empty
    # Note that the client may prefer to intercept incorrect day values such as
    # the one used for this test.
    def test_agenda_for_missing_day(self, calendar):
        assert calendar.print_agenda(5, 99) == "No Meetings booked on this date.\n\n"

    # UT95: Test that the agenda is empty after a schedule clear.
    # Expected outcome: Agenda is empty
    def test_agenda_after_clear_is_empty(self, calendar):
        calendar.add_meeting(meeting())
        calendar.clear_schedule(5, 10)
        assert calendar.print_agenda(5, 10) == "No Meetings booked on this date.\n\n"

    # UT96: Test that the placeholder returns the placeholder values in the agenda
    # Expected outcome: Agenda shows "day does not exist"
    def test_agenda_for_placeholder_day_lists_placeholder(self, calendar):
        agenda = calendar.print_agenda(2, 30)
        assert agenda.startswith("Agenda for 2/30 are as follows:\n")
        assert "Day does not exist" in agenda

    # UT97: Test that the earlier print_agenda function in the Calendar 
    #       class is unreachable
    # Expected outcome: Raise TypeError
    def test_month_only_overload_is_shadowed(self, calendar):
        with pytest.raises(TypeError):
            calendar.print_agenda(5)

    # UT98: Test to mark the two print_agenda functions.
    # Expected outcome: xfail
    @pytest.mark.xfail(strict=True, reason="print_agenda(month) is shadowed by print_agenda(month, day")
    def test_month_agenda_should_work(self, calendar):
        calendar.add_meeting(meeting())
        assert "Agenda for 5" in calendar.print_agenda(5)


# -------------- Section 6: get_meeting --------------

    # UT99: Test to check that get_meeting completes successfully
    # Expected outcome: Meetings are shown successfully
    def test_get_meeting_pass(self, calendar):
        a = meeting(start=1, end=2)
        b = meeting(start=5, end=6)

        calendar.add_meeting(a)
        calendar.add_meeting(b)

        assert calendar.get_meeting(5, 10, 0) is a
        assert calendar.get_meeting(5, 10, 1) is b

    # UT100: Test to check that invalid indices are rejected
    # Expected outcome: Raise IndexError
    def test_get_meeting_bad_index(self, calendar):
        with pytest.raises(IndexError):
            calendar.get_meeting(5, 10, 0)

# -------------- Section 6: remove_meeting --------------

    # UT101: Test to check that remove_meeting completes successfully
    # Expected outcome: Meetings removed successfully
    def test_remove_meeting_pass(self, calendar):
        a = meeting(start=1, end=2)
        b = meeting(start=5, end=6)
        calendar.add_meeting(a)
        calendar.add_meeting(b)
        calendar.remove_meeting(5, 10, 0)
        assert calendar.occupied[5][10] == [b]

    # UT102: Test to check that newly free slots can be rebooked
    # Expected outcome: Successful booking
    def test_removed_slot_can_be_rebooked(self, calendar):
        calendar.add_meeting(meeting(start=9, end=12))
        calendar.remove_meeting(5, 10, 0)
        calendar.add_meeting(meeting(start=9, end=12)) 
        assert len(calendar.occupied[5][10]) == 1

    # UT103: Test to check that invalid indices are rejected
    # Expected outcome: Raise IndexErrpr
    def test_remove_meeting_bad_index(self, calendar):
        with pytest.raises(IndexError):
            calendar.remove_meeting(5, 10, 3)

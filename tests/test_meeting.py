"""
This file houses the structural tests for the Meeting class.
According to the CFG, this class is somewhat more complex than 
Person and Room but less so than Calendar.
"""

# import the required classes from logic
import pytest

from logic.Meeting import Meeting
from logic.Person import Person
from logic.Room import Room
from logic.Organization import Organization

@pytest.fixture
def org():
    return Organization()

# Create the constructor
class TestMeetingConstructor:

    # UT-104: Test that a new meeting with only the minimum
    #         required changes made is constructed with default values
    # Expected outcome: Meeting is created successfully
    def test_defaults(self):
        m = Meeting(3, 15)
        assert m.get_month() == 3
        assert m.get_day() == 15
        assert m.get_start_time() == 0       
        assert m.get_end_time() == 23        
        assert m.get_attendees() == []     
        assert m.get_room() is None
        assert m.get_description() == ""

    # UT105: Test that default attendee lists are not shared between Meeting objects
    # Expected outcome: Attendee lists are separate
    def test_default_attendee_lists_are_not_shared(self):
        m1 = Meeting(1, 1)
        m2 = Meeting(1, 2)
        m1.add_attendee(Person("A"))
        assert m2.get_attendees() == []

    # UT106: Test that the arguments are used as is (attendees is not None)
    # Expected outcome: Attendee list is used correctly
    def test_all_arguments_supplied(self):
        p = Person("Alice")
        r = Room("R1")
        m = Meeting(5, 20, 9, 11, [p], r, "Standup")
        assert (m.get_month(), m.get_day()) == (5, 20)
        assert (m.get_start_time(), m.get_end_time()) == (9, 11)
        assert m.get_attendees() == [p]
        assert m.get_room() is r
        assert m.get_description() == "Standup"

    # UT107: Test that a supplied empty list is not replaced (as it is not None)
    # Expected outcome: get_attendees is an empty list 
    def test_empty_list_is_kept_not_replaced(self):
        lst = []
        m = Meeting(1, 1, attendees=lst)
        assert m.get_attendees() is lst

# -------------- Section 2: Attendee management --------------

class TestMeetingAttendees:
    def test_add_attendee(self):
        m = Meeting(1, 1)
        p = Person("Bob")
        m.add_attendee(p)
        assert m.get_attendees() == [p]

    # UT108: Test that adding multiple attendees does not change list order
    # Expected outcome: List order remains unchanged
    def test_add_multiple_attendees_keeps_order(self):
        m = Meeting(1, 1)
        a = Person("A")
        b = Person("B")
        m.add_attendee(a)
        m.add_attendee(b)
        assert m.get_attendees() == [a, b]

    # UT109: Test that remove_attendee completes successfully
    # Expected outcome: remove_attendee completes without errors
    def test_remove_attendee_pass(self):
        a = Person("A")
        b = Person("B")
        m = Meeting(1, 1, attendees=[a, b])
        m.remove_attendee(a)
        assert m.get_attendees() == [b]

    # UT110: Test that attendees not in the meeting cannot be removed
    # Expected outcome: Non-present attendees raise a ValueError
    def test_remove_nonpresent_attendee(self):
        m = Meeting(1, 1)
        with pytest.raises(ValueError):
            m.remove_attendee(Person("Ghost"))

# -------------- Section 3: String information --------------

class TestMeetingStr:

    # UT111: Test that a filled room with attendees returns the correct string
    # Expected outcome: Correct string is returned
    def test_str_with_room_and_attendees(self, org):
        helen = org.get_employee("Helen West")
        mike = org.get_employee("Mike Smith")
        room = org.get_room("ML21.520")
        m = Meeting(4, 12, 10, 12, [helen, mike], room, "Review")
        assert str(m) == (
            "Month: 4, Day: 12, Time slot: 10 - 12, Room No: ML21.520: Review\n"
            "Attending: Helen West, Mike Smith"
        )

    # UT112: Test that a room with a single attendee returns the correct string
    # Expected outcome: Correct string is returned
    def test_str_with_single_attendee_has_no_separator(self, org):
        m = Meeting(4, 12, 10, 12, [org.get_employee("Rose Austin")], org.get_room("JO1.230"), "x")
        assert str(m).endswith("Attending: Rose Austin")
        assert "," not in str(m).split("Attending:")[1]

    # UT113: Test that a meeting with no room and no attendees returns the correct string
    # Expected outcome: Correct string is returned
    def test_str_without_room_and_without_attendees(self):
        m = Meeting(1, 2, 3, 4, description="Solo")
        assert str(m) == (
            "Month: 1, Day: 2, Time slot: 3 - 4, Room No: N/A: Solo\n"
            "Attending: No attendees"
        )

    # UT114: Test that a meeting with a room and no attendees returns the correct string
    # Expected outcome: Correct string is returned
    def test_str_room_present_but_no_attendees(self, org):
        m = Meeting(1, 2, 3, 4, room=org.get_room("ML13.213"), description="d")
        assert "Room No: ML13.213" in str(m)
        assert str(m).endswith("Attending: No attendees")

    # UT115: Test that a meeting with attendees but no room returns the correct string
    # Expected outcome: Correct string is returned
    def test_str_attendees_present_but_no_room(self, org):
        m = Meeting(1, 2, 3, 4, attendees=[org.get_employee("Edith Cowan")], description="d")
        assert "Room No: N/A" in str(m)
        assert str(m).endswith("Attending: Edith Cowan")

    # UT116: Test that __str__ works for every predefined room
    # Expected outcome: Correct string is returned
    @pytest.mark.parametrize("room_id", [r.get_id() for r in Organization().get_rooms()])
    def test_str_for_every_valid_room(self, org, room_id):
        m = Meeting(1, 2, 3, 4, room=org.get_room(room_id), description="d")
        assert f"Room No: {room_id}: d" in str(m)

    # UT117: Test that __str__ lists every predefined person
    # Expected outcome: Correct string is returned
    def test_str_with_all_valid_attendees(self, org):
        people = org.get_employees()
        m = Meeting(1, 2, 3, 4, attendees=people, description="All hands")
        expected = "Attending: " + ", ".join(p.get_name() for p in people)
        assert str(m).endswith(expected)
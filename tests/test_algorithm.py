"""Tests for the matching algorithm."""

from ..algorithm.matching import Matching


def test_basic_matching_without_conflicts():
    """Tests a basic matching without any conflicts."""
    students_preference = {
        "Student_1": ["company_1"],
        "Student_2": ["company_2"],
        "Student_3": ["company_3"],
    }
    employer_preference = {
        "company_1": {"positions": 1, "Student_1": 1},
        "company_2": {"positions": 1, "Student_2": 1},
        "company_3": {"positions": 1, "Student_3": 1},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        [],
        {
            "company_1": ["Student_1"],
            "company_2": ["Student_2"],
            "company_3": ["Student_3"],
        },
    )

    assert result == expected


def test_students_exceed_company_positions():
    """Tests a scenario where students exceed the number of positions available."""
    students_preference = {
        "Student_1": ["company_1"],
        "Student_2": ["company_1"],
        "Student_3": ["company_1"],
    }
    employer_preference = {
        "company_1": {
            "positions": 1,
            "Student_1": 2,
            "Student_2": 1,
            "Student_3": 3,
        },
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        ["Student_1", "Student_3"],
        {
            "company_1": ["Student_2"],
        },
    )

    assert result == expected


def test_replacing_weaker_match():
    """Tests a scenario where a weaker match is replaced by a stronger one."""
    students_preference = {
        "Student_1": ["company_1"],
        "Student_2": ["company_1"],
    }
    employer_preference = {
        "company_1": {"positions": 1, "Student_2": 1, "Student_1": 2},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        ["Student_1"],
        {
            "company_1": ["Student_2"],
        },
    )

    assert result == expected


def test_no_positions_left_for_students():
    """Tests a scenario where there are no positions left for students."""
    students_preference = {
        "Student_1": ["company_1"],
        "Student_2": ["company_1"],
        "Student_3": ["company_2"],
    }
    employer_preference = {
        "company_1": {"positions": 1, "Student_1": 1, "Student_2": 2},
        "company_2": {"positions": 0},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        ["Student_2", "Student_3"],
        {
            "company_1": ["Student_1"],
        },
    )

    assert result == expected


def test_matching_with_multiple_preferences():
    """Tests a scenario where students and employers have multiple preferences."""
    students_preference = {
        "Student_1": ["company_1", "company_2"],
        "Student_2": ["company_1", "company_2"],
        "Student_3": ["company_2"],
        "Student_4": ["company_3", "company_1"],
    }
    employer_preference = {
        "company_1": {"positions": 1, "Student_1": 1, "Student_2": 2},
        "company_2": {
            "positions": 2,
            "Student_3": 1,
            "Student_2": 2,
            "Student_1": 3,
        },
        "company_3": {"positions": 1, "Student_4": 1},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        [],
        {
            "company_1": ["Student_1"],
            "company_2": ["Student_2", "Student_3"],
            "company_3": ["Student_4"],
        },
    )

    assert result == expected


def test_student_reassigned_due_to_higher_priority():
    """Tests a scenario where a student is reassigned due to higher priority."""
    students_preference = {
        "Student_1": ["company_1"],
        "Student_2": ["company_1"],
        "Student_3": ["company_1"],
    }
    employer_preference = {
        "company_1": {
            "positions": 1,
            "Student_1": 1,
            "Student_2": 3,
            "Student_3": 2,
        },
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        ["Student_2", "Student_3"],
        {
            "company_1": ["Student_1"],
        },
    )

    assert result == expected


def test_unequal_positions_distribution():
    """Tests a scenario where employers have unequal positions."""
    students_preference = {
        "Student_1": ["company_1"],
        "Student_2": ["company_1", "company_2"],
        "Student_4": ["company_2"],
        "Student_3": ["company_2"],
    }
    employer_preference = {
        "company_1": {"positions": 2, "Student_1": 1, "Student_2": 2},
        "company_2": {"positions": 1, "Student_3": 1, "Student_4": 2},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        ["Student_4"],
        {
            "company_1": ["Student_1", "Student_2"],
            "company_2": ["Student_3"],
        },
    )

    assert result == expected


def test_student_prefers_multiple_companies():
    """Tests a scenario where a student prefers multiple companies."""
    students_preference = {
        "Student_1": ["company_1", "company_2"],
        "Student_2": ["company_1", "company_2"],
    }
    employer_preference = {
        "company_1": {"positions": 1, "Student_2": 1, "Student_1": 2},
        "company_2": {"positions": 1, "Student_1": 1, "Student_2": 2},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        [],
        {
            "company_1": ["Student_2"],
            "company_2": ["Student_1"],
        },
    )

    assert result == expected


def test_confusing_preference_leading_to_correct_match():
    """Tests a scenario where a student's preference is confusing."""
    students_preference = {
        "Student_1": ["company_2", "company_1"],
        "Student_2": ["company_2"],
        "Student_3": ["company_1"],
        "Student_4": ["company_1"],
    }
    employer_preference = {
        "company_1": {"positions": 2, "Student_3": 1, "Student_4": 2},
        "company_2": {"positions": 1, "Student_1": 1, "Student_2": 2},
    }
    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()
    expected = (
        ["Student_2"],
        {
            "company_1": ["Student_3", "Student_4"],
            "company_2": ["Student_1"],
        },
    )

    assert result == expected


def test_multiple_unmapped_students():
    """Test when there are multiple students that could not be mapped."""
    students_preference = {
        "Student_1": ["company_2", "company_3"],
        "Student_2": ["company_1", "company_4", "company_5"],
        "Student_3": ["company_1", "company_2", "company_6"],
        "Student_4": ["company_3", "company_5"],
        "Student_5": ["company_2", "company_3", "company_7"],
        "Student_6": ["company_5", "company_8"],
        "Student_7": ["company_1", "company_4"],
        "Student_8": ["company_7", "company_9", "company_5"],
        "Student_9": ["company_1", "company_2"],
        "Student_10": ["company_8", "company_10", "company_9"],
    }

    employer_preference = {
        "company_1": {
            "positions": 2,
            "Student_2": 1,
            "Student_3": 2,
            "Student_9": 3,
            "Student_5": 4,
            "Student_1": 5,
        },
        "company_2": {
            "positions": 0,
            "Student_1": 1,
            "Student_5": 2,
            "Student_3": 3,
            "Student_10": 4,
            "Student_8": 5,
            "Student_4": 6,
        },
        "company_3": {
            "positions": 0,
            "Student_4": 1,
            "Student_1": 2,
            "Student_2": 3,
            "Student_9": 4,
            "Student_8": 5,
        },
        "company_4": {
            "positions": 0,
            "Student_2": 1,
            "Student_7": 2,
            "Student_5": 3,
            "Student_1": 4,
            "Student_3": 5,
        },
        "company_5": {
            "positions": 1,
            "Student_6": 1,
            "Student_4": 2,
            "Student_2": 3,
            "Student_10": 4,
        },
        "company_6": {
            "positions": 1,
            "Student_3": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_9": 4,
        },
        "company_7": {
            "positions": 1,
            "Student_5": 1,
            "Student_8": 2,
            "Student_1": 3,
            "Student_3": 4,
        },
        "company_8": {
            "positions": 0,
            "Student_10": 1,
            "Student_6": 2,
            "Student_2": 3,
            "Student_3": 4,
        },
        "company_9": {
            "positions": 1,
            "Student_2": 1,
            "Student_4": 2,
            "Student_1": 3,
        },
        "company_10": {
            "positions": 1,
            "Student_10": 1,
            "Student_5": 2,
            "Student_6": 3,
            "Student_8": 4,
        },
    }

    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()

    expected = (
        ["Student_1", "Student_4", "Student_7", "Student_9"],
        {
            "company_1": ["Student_2", "Student_3"],
            "company_5": ["Student_6"],
            "company_7": ["Student_5"],
            "company_9": ["Student_8"],
            "company_10": ["Student_10"],
        },
    )

    assert result == expected


def test_larger_set_matching_scenario():
    """Test a larger set of students and employers to find the best match."""
    students_preference = {
        "Student_1": ["company_2", "company_3", "company_6", "company_7"],
        "Student_2": ["company_1", "company_4", "company_5", "company_9"],
        "Student_3": ["company_1", "company_2", "company_6", "company_10"],
        "Student_4": ["company_3", "company_5", "company_6", "company_9"],
        "Student_5": ["company_2", "company_7", "company_8"],
        "Student_6": ["company_5", "company_8", "company_10"],
        "Student_7": ["company_1", "company_4", "company_7"],
        "Student_8": ["company_7", "company_9", "company_5", "company_3"],
        "Student_9": ["company_1", "company_2", "company_8"],
        "Student_10": ["company_8", "company_10", "company_9"],
        "Student_11": ["company_2", "company_6", "company_5"],
        "Student_12": ["company_10", "company_4", "company_7", "company_8"],
        "Student_13": ["company_1", "company_6", "company_7"],
        "Student_14": ["company_4", "company_5", "company_10"],
        "Student_15": ["company_6", "company_8", "company_9", "company_3"],
    }

    employer_preference = {
        "company_1": {
            "positions": 3,
            "Student_2": 1,
            "Student_3": 2,
            "Student_9": 3,
            "Student_7": 4,
            "Student_13": 5,
        },
        "company_2": {
            "positions": 1,
            "Student_1": 1,
            "Student_3": 2,
            "Student_11": 3,
            "Student_9": 4,
            "Student_5": 5,
        },
        "company_3": {
            "positions": 1,
            "Student_4": 1,
            "Student_8": 2,
            "Student_1": 3,
            "Student_15": 4,
        },
        "company_4": {
            "positions": 2,
            "Student_2": 1,
            "Student_7": 2,
            "Student_12": 3,
            "Student_14": 4,
        },
        "company_5": {
            "positions": 1,
            "Student_4": 1,
            "Student_6": 2,
            "Student_14": 3,
            "Student_8": 4,
            "Student_15": 5,
        },
        "company_6": {
            "positions": 1,
            "Student_3": 1,
            "Student_1": 2,
            "Student_11": 3,
            "Student_13": 4,
        },
        "company_7": {
            "positions": 2,
            "Student_5": 1,
            "Student_12": 2,
            "Student_1": 3,
            "Student_8": 4,
        },
        "company_8": {
            "positions": 2,
            "Student_6": 1,
            "Student_5": 2,
            "Student_10": 3,
            "Student_15": 4,
        },
        "company_9": {
            "positions": 1,
            "Student_2": 1,
            "Student_4": 2,
            "Student_10": 3,
            "Student_8": 4,
        },
        "company_10": {
            "positions": 2,
            "Student_10": 1,
            "Student_12": 2,
            "Student_14": 3,
            "Student_6": 4,
        },
    }

    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()

    expected = (
        ["Student_13"],
        {
            "company_2": ["Student_1"],
            "company_1": ["Student_2", "Student_3", "Student_9"],
            "company_3": ["Student_4"],
            "company_7": ["Student_5", "Student_8"],
            "company_5": ["Student_6"],
            "company_4": ["Student_7", "Student_14"],
            "company_8": ["Student_10", "Student_15"],
            "company_6": ["Student_11"],
            "company_10": ["Student_12"],
        },
    )

    assert result == expected

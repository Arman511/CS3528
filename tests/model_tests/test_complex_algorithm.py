"""Tests for the matching algorithm."""

import os
import sys
import time
import random

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from algorithm.matching import Matching


def test_complex_student_employer_preferences():
    """Tests a complex scenario with multiple students and employers."""
    students_preference = {
        "Student_1": ["company_1", "company_2", "company_3"],
        "Student_2": ["company_2"],
        "Student_3": ["company_5", "company_4", "company_3"],
        "Student_4": ["company_1", "company_5", "company_6"],
        "Student_5": ["company_6", "company_7", "company_8"],
        "Student_6": ["company_4", "company_5", "company_9"],
        "Student_7": ["company_2", "company_3", "company_7"],
        "Student_8": ["company_1", "company_6", "company_10"],
        "Student_9": ["company_3", "company_8", "company_9"],
        "Student_10": ["company_2", "company_5", "company_6"],
    }

    employer_preference = {
        "company_1": {
            "positions": 2,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_3": 6,
            "Student_5": 7,
            "Student_9": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
        "company_2": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_3": 5,
            "Student_2": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
        "company_3": {
            "positions": 2,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_8": 6,
            "Student_3": 7,
            "Student_5": 8,
            "Student_9": 9,
            "Student_6": 10,
        },
        "company_4": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_3": 5,
            "Student_2": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
        "company_5": {
            "positions": 2,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_3": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
        "company_6": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_5": 6,
            "Student_8": 7,
            "Student_9": 8,
            "Student_3": 9,
            "Student_6": 10,
        },
        "company_7": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_3": 5,
            "Student_2": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_6": 9,
            "Student_8": 10,
        },
        "company_8": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_3": 5,
            "Student_2": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
        "company_9": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_3": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
        "company_10": {
            "positions": 1,
            "Student_7": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_3": 6,
            "Student_9": 7,
            "Student_5": 8,
            "Student_8": 9,
            "Student_6": 10,
        },
    }

    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()

    expected = (
        ["Student_2"],
        {
            "company_1": ["Student_1", "Student_4"],
            "company_2": ["Student_7"],
            "company_5": ["Student_3", "Student_10"],
            "company_6": ["Student_5"],
            "company_4": ["Student_6"],
            "company_3": ["Student_9"],
            "company_10": ["Student_8"],
        },
    )
    assert result == expected


def test_complex_student_employer_preferences_v2():
    """Tests a complex scenario with multiple students and employers."""
    students_preference = {
        "Student_1": ["company_1", "company_2", "company_3"],
        "Student_2": ["company_2", "company_4"],
        "Student_3": ["company_1", "company_5", "company_6"],
        "Student_4": ["company_3", "company_2", "company_1"],
        "Student_5": ["company_7", "company_8", "company_4"],
        "Student_6": ["company_8", "company_9", "company_5"],
        "Student_7": ["company_1", "company_6"],
        "Student_8": ["company_5", "company_3", "company_2"],
        "Student_9": ["company_4", "company_7", "company_10"],
        "Student_10": ["company_2", "company_9", "company_8"],
    }

    employer_preference = {
        "company_1": {
            "positions": 2,
            "Student_1": 1,
            "Student_3": 2,
            "Student_4": 3,
            "Student_7": 4,
            "Student_5": 5,
            "Student_10": 6,
            "Student_9": 7,
            "Student_2": 8,
            "Student_6": 9,
            "Student_8": 10,
        },
        "company_2": {
            "positions": 2,
            "Student_2": 1,
            "Student_1": 2,
            "Student_4": 3,
            "Student_10": 4,
            "Student_6": 5,
            "Student_9": 6,
            "Student_8": 7,
            "Student_7": 8,
            "Student_5": 9,
            "Student_3": 10,
        },
        "company_3": {
            "positions": 1,
            "Student_4": 1,
            "Student_1": 2,
            "Student_8": 3,
            "Student_2": 4,
            "Student_10": 5,
            "Student_5": 6,
            "Student_6": 7,
            "Student_3": 8,
            "Student_9": 9,
            "Student_7": 10,
        },
        "company_4": {
            "positions": 2,
            "Student_2": 1,
            "Student_5": 2,
            "Student_9": 3,
            "Student_1": 4,
            "Student_4": 5,
            "Student_3": 6,
            "Student_8": 7,
            "Student_10": 8,
            "Student_6": 9,
            "Student_7": 10,
        },
        "company_5": {
            "positions": 2,
            "Student_3": 1,
            "Student_6": 2,
            "Student_8": 3,
            "Student_1": 4,
            "Student_2": 5,
            "Student_4": 6,
            "Student_10": 7,
            "Student_5": 8,
            "Student_7": 9,
            "Student_9": 10,
        },
        "company_6": {
            "positions": 1,
            "Student_1": 1,
            "Student_2": 2,
            "Student_7": 3,
            "Student_4": 4,
            "Student_3": 5,
            "Student_9": 6,
            "Student_10": 7,
            "Student_8": 8,
            "Student_5": 9,
            "Student_6": 10,
        },
        "company_7": {
            "positions": 1,
            "Student_5": 1,
            "Student_9": 2,
            "Student_3": 3,
            "Student_2": 4,
            "Student_4": 5,
            "Student_8": 6,
            "Student_10": 7,
            "Student_6": 8,
            "Student_1": 9,
            "Student_7": 10,
        },
        "company_8": {
            "positions": 1,
            "Student_6": 1,
            "Student_1": 2,
            "Student_2": 3,
            "Student_5": 4,
            "Student_3": 5,
            "Student_10": 6,
            "Student_7": 7,
            "Student_8": 8,
            "Student_4": 9,
            "Student_9": 10,
        },
        "company_9": {
            "positions": 1,
            "Student_6": 1,
            "Student_10": 2,
            "Student_5": 3,
            "Student_2": 4,
            "Student_7": 5,
            "Student_1": 6,
            "Student_3": 7,
            "Student_8": 8,
            "Student_4": 9,
            "Student_9": 10,
        },
        "company_10": {
            "positions": 1,
            "Student_4": 1,
            "Student_2": 2,
            "Student_9": 3,
            "Student_5": 4,
            "Student_7": 5,
            "Student_3": 6,
            "Student_1": 7,
            "Student_10": 8,
            "Student_6": 9,
            "Student_8": 10,
        },
    }

    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()

    expected = (
        [],
        {
            "company_1": ["Student_1", "Student_3"],
            "company_2": ["Student_2", "Student_10"],
            "company_3": ["Student_4"],
            "company_7": ["Student_5"],
            "company_8": ["Student_6"],
            "company_6": ["Student_7"],
            "company_5": ["Student_8"],
            "company_4": ["Student_9"],
        },
    )

    assert result == expected


def test_complex_student_employer_preferences_v3():
    """Tests a complex scenario with multiple students and employers."""
    students_preference = {
        "Student_1": ["company_1", "company_2"],
        "Student_2": ["company_1", "company_3", "company_4"],
        "Student_3": ["company_5", "company_6"],
        "Student_4": ["company_2", "company_7", "company_5"],
        "Student_5": ["company_3", "company_4", "company_8"],
        "Student_6": ["company_1", "company_8", "company_3"],
        "Student_7": ["company_5", "company_6", "company_9"],
        "Student_8": ["company_2", "company_3"],
        "Student_9": ["company_7", "company_4"],
        "Student_10": ["company_1", "company_9", "company_10"],
    }

    employer_preference = {
        "company_1": {
            "positions": 2,
            "Student_1": 1,
            "Student_2": 2,
            "Student_6": 3,
            "Student_10": 4,
            "Student_4": 5,
            "Student_8": 6,
        },
        "company_2": {
            "positions": 1,
            "Student_4": 1,
            "Student_1": 2,
            "Student_8": 3,
            "Student_5": 4,
            "Student_3": 5,
            "Student_10": 6,
            "Student_2": 7,
            "Student_7": 8,
            "Student_9": 9,
        },
        "company_3": {
            "positions": 2,
            "Student_10": 1,
            "Student_2": 2,
            "Student_6": 3,
            "Student_8": 4,
            "Student_5": 5,
            "Student_1": 6,
            "Student_3": 7,
            "Student_4": 8,
            "Student_7": 9,
        },
        "company_4": {
            "positions": 2,
            "Student_5": 1,
            "Student_9": 2,
            "Student_2": 3,
            "Student_1": 4,
            "Student_10": 5,
            "Student_6": 6,
            "Student_3": 7,
            "Student_7": 8,
            "Student_8": 9,
        },
        "company_5": {
            "positions": 1,
            "Student_3": 1,
            "Student_4": 2,
            "Student_7": 3,
            "Student_1": 4,
            "Student_2": 5,
            "Student_8": 6,
        },
        "company_6": {
            "positions": 2,
            "Student_3": 1,
            "Student_7": 2,
            "Student_5": 3,
            "Student_10": 4,
            "Student_2": 5,
            "Student_1": 6,
            "Student_4": 7,
            "Student_9": 8,
        },
        "company_7": {
            "positions": 1,
            "Student_4": 1,
            "Student_9": 2,
            "Student_1": 3,
            "Student_6": 4,
            "Student_10": 5,
            "Student_2": 6,
            "Student_5": 7,
            "Student_8": 8,
        },
        "company_8": {
            "positions": 1,
            "Student_3": 1,
            "Student_5": 2,
            "Student_1": 3,
            "Student_2": 4,
            "Student_9": 5,
            "Student_10": 6,
        },
        "company_9": {
            "positions": 1,
            "Student_7": 1,
            "Student_10": 2,
            "Student_1": 3,
            "Student_2": 4,
            "Student_3": 5,
            "Student_8": 6,
        },
    }

    match = Matching(students_preference, employer_preference)
    result = match.find_best_match()

    expected = (
        [],
        {
            "company_1": ["Student_1", "Student_2"],
            "company_5": ["Student_3"],
            "company_2": ["Student_4"],
            "company_3": ["Student_8", "Student_6"],
            "company_6": ["Student_7"],
            "company_4": ["Student_5"],
            "company_7": ["Student_9"],
            "company_9": ["Student_10"],
        },
    )
    assert result == expected


def test_complex_student_employer_preferences_v4():
    """Test a complex matching scenario."""
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
            "positions": 2,
            "Student_1": 1,
            "Student_5": 2,
            "Student_3": 3,
            "Student_10": 4,
            "Student_8": 5,
            "Student_4": 6,
        },
        "company_3": {
            "positions": 1,
            "Student_4": 1,
            "Student_1": 2,
            "Student_2": 3,
            "Student_9": 4,
            "Student_8": 5,
        },
        "company_4": {
            "positions": 2,
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
            "positions": 2,
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
        ["Student_9"],
        {
            "company_2": ["Student_1", "Student_5"],
            "company_1": ["Student_2", "Student_3"],
            "company_3": ["Student_4"],
            "company_5": ["Student_6"],
            "company_4": ["Student_7"],
            "company_7": ["Student_8"],
            "company_8": ["Student_10"],
        },
    )

    assert result == expected


def test_large_scale_matching_under_30_seconds():
    """Tests the matching algorithm with 5000 students and enough employers under 30 seconds."""
    num_students = 5000
    num_companies = 1000
    student_ids = [f"Student_{i+1}" for i in range(num_students)]
    company_ids = [f"company_{i+1}" for i in range(num_companies)]

    # Generate random student preferences
    students_preference = {}
    for student in student_ids:
        preferred_companies = random.sample(company_ids, k=random.randint(5, 10))
        students_preference[student] = preferred_companies

    # Generate random employer preferences
    employer_preference = {}
    for company in company_ids:
        positions = random.randint(2, 10)  # Each company offers 2-10 positions
        ranked_students = random.sample(student_ids, k=len(student_ids))
        preference = {student: rank + 1 for rank, student in enumerate(ranked_students)}
        preference["positions"] = positions
        employer_preference[company] = preference

    # Run the matching algorithm and time it
    match = Matching(students_preference, employer_preference)

    start_time = time.time()
    result = match.find_best_match()
    end_time = time.time()

    duration = end_time - start_time
    assert duration < 30, f"Matching took too long: {duration:.2f} seconds"

"""
The matching algorithm is a stable marriage algorithm that matches students 
to placements based on their preferences. The algorithm is implemented in the 
`Matching` class. The `find_best_match` method finds the best match for students and placements. 
"""

from typing import List, Dict, Tuple


class Matching:
    """Class to match students to placements based on their preferences."""

    def __init__(
        self,
        student_rank: Dict[str, List[str]],
        placement_rank: Dict[str, Dict[str, int]],
    ):
        # Students' preferences
        self.student_rank = student_rank
        # Employers' rankings, includes "positions" key
        self.placement_rank = placement_rank
        # To store the final matches
        self.potential_match: Dict[str, List[str]] = {}
        # To store the final matches (Unmatched, Matched)
        self.final_result: Tuple[List[str], Dict[str, List[str]]] = ([], {})

    def find_best_match(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """Find the best match for students and placements."""
        students = list(self.student_rank.keys())  # List of unmatched students
        unmapped = []  # List of students who cannot be matched (no more preferences)
        # Keep track of employers' current engagements
        placement_current_match: Dict[str, List[str]] = {
            placement: [] for placement in self.placement_rank.keys()
        }

        # print("Initial state:")
        # print(f"Students: {students}")
        # print(f"Employers' current matches: {placement_current_match}")

        while students:
            student = students.pop(0)  # Pick the next unmatched student
            # print(f"\nProcessing student: {student}")

            if not self.student_rank[student]:  # If student has no more preferences
                # print(f"Student {student} has no more preferences and is unmapped.")
                unmapped.append(student)
                continue

            choice = self.student_rank[student].pop(0)
            # print(f"{student} prefers placement: {choice}")

            # Check current matches of the chosen employer
            current_matches = placement_current_match[choice]
            positions = self.placement_rank[choice]["positions"]

            # If there are positions available, add the student
            if (
                len(current_matches) < positions
                and student in self.placement_rank[choice]
            ):
                # print(f"{choice} has available positions. Adding {student}.")
                placement_current_match[choice].append(student)
                self.potential_match[choice] = placement_current_match[choice]

            else:
                # print(f"{choice} is full or {student} is not ranked by the employer.")
                if current_matches:
                    # print(f"Current matches at {choice}: {current_matches}")

                    # Find the weakest match using the employer's ranking
                    weakest_match = current_matches[-1]  # Get the least preferred match
                    weakest_match_rank = self.placement_rank[choice][weakest_match]
                    index = len(current_matches) - 1

                    for match in current_matches:
                        if self.placement_rank[choice][match] > weakest_match_rank:
                            weakest_match = match
                            weakest_match_rank = self.placement_rank[choice][match]
                            index = current_matches.index(weakest_match)

                    # Check if the student is in the employer's ranking
                    if student in self.placement_rank[choice]:
                        new_candidate_rank = self.placement_rank[choice][student]
                        # print(
                        #     f"Comparing {student} (rank {new_candidate_rank}) with weakest match {weakest_match} (rank {weakest_match_rank})."
                        # )

                        # If new student is ranked higher (lower number), replace the weakest match
                        if new_candidate_rank < weakest_match_rank:
                            # print(
                            #     f"{student} is ranked higher than {weakest_match}. Replacing."
                            # )
                            placement_current_match[choice][
                                index
                            ] = student  # Replace weakest match
                            self.potential_match[choice] = placement_current_match[
                                choice
                            ]
                            students.insert(
                                0, weakest_match
                            )  # Re-add the replaced student to the unmatched list
                        else:
                            # print(
                            #     f"{student} is ranked lower than {weakest_match}. Rejected."
                            # )
                            students.insert(
                                0, student
                            )  # Add student back to the unmatched list
                    else:
                        # print(f"{student} is not ranked by {choice}. Rejected.")
                        students.insert(
                            0, student
                        )  # Re-add student to the unmatched list
                else:
                    # print(
                    # f"{choice} has no current matches. {student} has not been ranked by {choice}."
                    # )
                    students.insert(0, student)

        self.final_result = (unmapped, self.potential_match)
        # print("\nFinal result:")
        # print(f"Unmapped students: {self.final_result[0]}")
        # print(f"Matched students: {self.final_result[1]}")
        return self.final_result

    def get_matches(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """Get final result."""
        # print("\nReturning final matches:")
        # print(f"Unmapped: {self.final_result[0]}")
        # print(f"Matched: {self.final_result[1]}")
        return self.final_result

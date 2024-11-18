from typing import List, Dict, Tuple


class Matching:
    def __init__(
        self,
        student_rank: Dict[str, List[str]],
        placement_rank: Dict[str, Dict[str, int]],
    ):
        self.student_rank = student_rank  # Students' preferences
        self.placement_rank = (
            placement_rank  # Employers' rankings, includes "positions" key
        )
        self.potential_match = {}  # To store the final matches
        self.final_result = []  # To store the final matches (Unmatched, Matched)

    def find_best_match(self) -> Tuple[List[str], Dict[str, List[str]]]:
        """Find the best match for students and placements."""
        mapped = list(self.student_rank.keys())  # List of unmatched students
        unmapped = []  # List of can not be matched students (no more preferences)
        # Keep track of employers' current engagements
        placement_current_match: Dict[str, List[str]] = {
            placement: [] for placement in self.placement_rank.keys()
        }
        while mapped:
            student = mapped.pop(0)  # Pick the next unmatched student
            if not self.student_rank[student]:  # If student has no more preferences
                unmapped.append(student)
                continue

            choice = self.student_rank[student].pop(0)

            # Check current matches of the chosen employer
            current_matches = placement_current_match[choice]

            # Positions available
            positions = self.placement_rank[choice]["positions"]

            # If there are positions available, add the student
            if len(current_matches) < positions:
                placement_current_match[choice].append(student)
                self.potential_match[choice] = placement_current_match[choice]

            else:
                if current_matches:
                    # Employer already has the maximum allowed matches, compare with the weakest match
                    weakest_match = current_matches[-1]  # Get the least preferred match
                    weakest_match_rank = self.placement_rank[choice][weakest_match]

                    # Check if the student is in the employer's ranking
                    if student in self.placement_rank[choice]:
                        new_candidate_rank = self.placement_rank[choice][student]

                        # If the new student is ranked higher (lower number), replace the weakest match
                        if new_candidate_rank < weakest_match_rank:
                            placement_current_match[choice][
                                -1
                            ] = student  # Replace weakest match
                            self.potential_match[choice] = placement_current_match[
                                choice
                            ]
                            mapped.insert(
                                0, weakest_match
                            )  # Re-add the replaced student to the unmatched list
                        else:
                            # Add student back to mapped if rejected
                            mapped.insert(0, student)

                    else:
                        # Handle case where student is not in employer ranking
                        mapped.insert(
                            0, student
                        )  # Re-add student back to the unmatched list
                else:
                    # If current_matches is empty, avoid accessing it
                    mapped.insert(0, student)

        self.final_result = [unmapped, self.potential_match]
        # print(f"Unmapped: {self.final_result[0]} \nMatched: {self.final_result[1]}")
        return self.final_result

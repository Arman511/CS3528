class Matching:
    def __init__(self, studentrank, employerank):
        self.studentrank = studentrank  # Students' preferences
        self.employerank = employerank  # Employers' rankings, includes "positions" key
        self.potential_match = {}  # To store the final matches
        self.final_result = []  # To store the final matches (Unmatched, Matched)

    def find_best_match(self):
        mapped = list(self.studentrank.keys())  # List of unmatched students
        unmapped = []  # List of can not be matched students (no more preferences)

        # Keep track of employers' current engagements
        employer_current_match = {employer: [] for employer in self.employerank.keys()}

        while mapped:
            student = mapped.pop(0)  # Pick the next unmatched student

            if not self.studentrank[student]:  # If student has no more preferences
                # print(f"{student} has no more preferences left.")
                unmapped.append(student)
                continue

            choice = self.studentrank[student].pop(0)

            # Check current matches of the chosen employer
            current_matches = employer_current_match[choice]

            # Positions available
            positions = self.employerank[choice]["positions"]

            # If there are positions available, add the student
            if len(current_matches) < positions:
                employer_current_match[choice].append(student)
                self.potential_match[choice] = employer_current_match[choice]
                # print(f"{student} matched with {choice}. Current matches: {employer_current_match[choice]}")
            else:
                if current_matches:
                    # Employer already has the maximum allowed matches, compare with the weakest match
                    weakest_match = current_matches[-1]  # Get the least preferred match
                    weakest_match_rank = self.employerank[choice][weakest_match]
                    
                    # Check if the student is in the employer's ranking
                    if student in self.employerank[choice]:
                        new_candidate_rank = self.employerank[choice][student]
                        
                        # If the new student is ranked higher (lower number), replace the weakest match
                        if new_candidate_rank < weakest_match_rank:
                            employer_current_match[choice][-1] = student  # Replace weakest match
                            self.potential_match[choice] = employer_current_match[choice]
                            mapped.insert(0, weakest_match)  # Re-add the replaced student to the unmatched list
                            # print(f"{student} replaces {weakest_match} at {choice}. Current matches: {employer_current_match[choice]}")
                        else:
                            # Add student back to mapped if rejected
                            mapped.insert(0, student)
                            # print(f"{student} was rejected by {choice}.")
                    else:
                        # Handle case where student is not in employer ranking
                        # print(f"{student} is not ranked by {choice}.")
                        mapped.insert(0, student)  # Re-add student back to the unmatched list
                else:
                    # If current_matches is empty, avoid accessing it
                    # print(f"{choice} has no matches yet.")
                    mapped.insert(0, student)


        self.final_result = [unmapped, self.potential_match]
        print(f"Unmapped: {self.final_result[0]} \nMatched: {self.final_result[1]}")
        return self.final_result

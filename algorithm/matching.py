class Matching:
    def __init__(self, studentrank, employerank):
        self.studentrank = studentrank  # Students' preferences
        self.employerank = employerank  # Employers' rankings, includes "positions" key
        self.potential_match = {}  # To store the final matches

    def find_best_match(self):
        mapped = list(self.studentrank.keys())  # List of unmatched students
        unmapped = []  # List of unmatched students

        # Keep track of employers' current engagements
        employer_current_match = {employer: [] for employer in self.employerank.keys()}

        while mapped:
            student = mapped.pop(0)  # Pick the next unmatched student

            if not self.studentrank[student]:  # If student has no more preferences
                print(f"{student} has no more preferences left.")
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
                print(f"{student} matched with {choice}. Current matches: {employer_current_match[choice]}")
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
                            print(f"{student} replaces {weakest_match} at {choice}. Current matches: {employer_current_match[choice]}")
                        else:
                            # Add student back to mapped if rejected
                            mapped.insert(0, student)
                            print(f"{student} was rejected by {choice}.")
                    else:
                        # Handle case where student is not in employer ranking
                        print(f"{student} is not ranked by {choice}.")
                        mapped.insert(0, student)  # Re-add student back to the unmatched list
                else:
                    # If current_matches is empty, avoid accessing it
                    print(f"{choice} has no matches yet.")
                    mapped.insert(0, student)


        print("Unmatched students: \n", unmapped)
        print("Best Matches:")
        print(self.potential_match)
        return self.potential_match
    


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
    "company_1": {"positions": 2, "Student_2": 1, "Student_3": 2, "Student_9": 3, "Student_5": 4, "Student_1": 5},
    "company_2": {"positions": 2, "Student_1": 1, "Student_5": 2, "Student_3": 3, "Student_10": 4, "Student_8": 5, "Student_4": 6},
    "company_3": {"positions": 1, "Student_4": 1, "Student_1": 2, "Student_2": 3, "Student_9": 4, "Student_8": 5},
    "company_4": {"positions": 2, "Student_2": 1, "Student_7": 2, "Student_5": 3, "Student_1": 4, "Student_3": 5},
    "company_5": {"positions": 1, "Student_6": 1, "Student_4": 2, "Student_2": 3, "Student_10": 4},
    "company_6": {"positions": 1, "Student_3": 1, "Student_1": 2, "Student_4": 3, "Student_9": 4},
    "company_7": {"positions": 1, "Student_5": 1, "Student_8": 2, "Student_1": 3, "Student_3": 4},
    "company_8": {"positions": 2, "Student_10": 1, "Student_6": 2, "Student_2": 3, "Student_3": 4},
    "company_9": {"positions": 1, "Student_2": 1, "Student_4": 2, "Student_1": 3},
    "company_10": {"positions": 1, "Student_10": 1, "Student_5": 2, "Student_6": 3, "Student_8": 4},
}

match = Matching(students_preference, employer_preference)
result = match.find_best_match()
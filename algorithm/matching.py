from employer_ranking import StudentRankingSystem

class Matching:
    def __init__(self, studentrank, employerank, employer_weights):
        self.studentrank = studentrank  # Students' preferences
        self.employerank = employerank  # Employers' rankings
        self.potential_match = {}  # To store the final matches
        self.employer_weights = employer_weights  # Weights for employer criteria
        

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
            positions = self.employer_weights[choice]["positions"]

            # If there are positions available, add the student
            if len(current_matches) < positions:
                employer_current_match[choice].append(student)
                self.potential_match[choice] = employer_current_match[choice]
                print(f"{student} matched with {choice}. Current matches: {employer_current_match[choice]}")
            else:
                # Check if the current_matches list is not empty before accessing its last element
                if current_matches:
                    # Employer already has the maximum allowed matches, compare with the weakest match
                    weakest_match = current_matches[-1]  # Get the least preferred match
                    weakest_match_rank = self.employerank[choice][weakest_match]
                    new_candidate_rank = self.employerank[choice][student]

                    # If the new student is ranked higher (lower number), replace the weakest match
                    if new_candidate_rank < weakest_match_rank:
                        employer_current_match[choice][-1] = student  # Replace weakest match
                        self.potential_match[choice] = employer_current_match[choice]
                        mapped.append(weakest_match)  # Re-add the replaced student to the unmatched list
                        print(f"{student} replaces {weakest_match} at {choice}. Current matches: {employer_current_match[choice]}")
                    else:
                        # Add student back to mapped if rejected
                        mapped.append(student)
                        print(f"{student} was rejected by {choice}.")
                else:
                    # If current_matches is empty, avoid accessing it
                    print(f"{choice} has no matches yet.")
                    mapped.insert(0, student)
                    
        print("Unmatched students: \n", unmapped)
        return self.potential_match


# Example student data
students = [
    {"name": "Student_1", "skills": 9, "experience": 7, "education": 8, "certifications": 3},
    {"name": "Student_2", "skills": 6, "experience": 5, "education": 6, "certifications": 2},
    {"name": "Student_3", "skills": 7, "experience": 4, "education": 5, "certifications": 1},
    {"name": "Student_4", "skills": 8, "experience": 6, "education": 7, "certifications": 3},
    {"name": "Student_5", "skills": 5, "experience": 5, "education": 6, "certifications": 4},
    {"name": "Student_6", "skills": 4, "experience": 3, "education": 5, "certifications": 2},
    {"name": "Student_7", "skills": 9, "experience": 7, "education": 8, "certifications": 5},
    {"name": "Student_8", "skills": 3, "experience": 8, "education": 4, "certifications": 2},
    {"name": "Student_9", "skills": 6, "experience": 5, "education": 5, "certifications": 1},
    {"name": "Student_10", "skills": 8, "experience": 6, "education": 7, "certifications": 3},
]

# Define employer weights for criteria
employer_weights = {
    "company_1": {"skills": 0.5, "experience": 0.2, "education": 0.1, "certifications": 0.2, "positions": 2},
    "company_2": {"skills": 0.6, "experience": 0.3, "education": 0.05, "certifications": 0.05, "positions": 1},
    "company_3": {"skills": 0.4, "experience": 0.4, "education": 0.1, "certifications": 0.1, "positions": 3},
    "company_4": {"skills": 0.7, "experience": 0.2, "education": 0.05, "certifications": 0.05, "positions": 2},
    "company_5": {"skills": 0.5, "experience": 0.25, "education": 0.15, "certifications": 0.1, "positions": 1},
    "company_6": {"skills": 0.3, "experience": 0.4, "education": 0.25, "certifications": 0.05, "positions": 3},
    "company_7": {"skills": 0.8, "experience": 0.1, "education": 0.05, "certifications": 0.05, "positions": 2},
    "company_8": {"skills": 0.6, "experience": 0.3, "education": 0.05, "certifications": 0.05, "positions": 1},
    "company_9": {"skills": 0.5, "experience": 0.3, "education": 0.1, "certifications": 0.1, "positions": 2},
    "company_10": {"skills": 0.4, "experience": 0.4, "education": 0.15, "certifications": 0.05, "positions": 3},
}

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

# Instantiate the ranking system and generate employer rankings
trial = StudentRankingSystem(students, employer_weights)
employer_preference = trial.display_ranking()  # Use rank_students to get rankings for matching

# Perform the matching process
match_trial = Matching(students_preference, employer_preference, employer_weights)
best_match = match_trial.find_best_match()

print("Best Matches:")
print(best_match)

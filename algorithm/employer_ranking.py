class StudentRankingSystem:
    def __init__(self, students, employers):
        # Initialize with student data and employer weights
        self.students = students
        self.employers = employers

    def calculate_score(self, student, employer_weights):
        # Calculate the score of a student based on employer's criteria weights
        score = 0
        for criterion, weight in employer_weights.items():
            if criterion == "positions":
                continue

            score += student[criterion] * weight
        return score  # Return as float for sorting

    def rank_students(self):
        # Dictionary to store rankings for each employer
        employer_rankings = {}

        # Loop over each employer and their weight criteria
        for employer, employer_weights in self.employers.items():
            student_scores = (
                []
            )  # Temporary list to store scores for the current employer

            # Calculate the score for each student based on the employer's weights
            for student in self.students:
                score = self.calculate_score(student, employer_weights)
                student_scores.append((student["name"], score))

            # Sort students by score in descending order
            student_scores.sort(key=lambda x: x[1], reverse=True)

            # Create a dictionary where student names are the keys and their rank (starting at 1) is the value
            ranking = {}
            for rank, (student_name, score) in enumerate(student_scores, 1):
                ranking[student_name] = rank

            # Store the ranking for this employer
            employer_rankings[employer] = ranking

        return employer_rankings

    def display_ranking(self):
        # Display the ranked students for each employer
        ranked_students = self.rank_students()
        # print("Ranked students for each employer (highest to lowest):")
        # for employer, rankings in ranked_students.items():
        #     print(f"{employer}:")
        #     for student, rank in rankings.items():
        #         print(f"  {student}: Rank {rank}")
        print(ranked_students)

        return ranked_students


# # Example student data
# students = [
#     {"name": "Student_1", "skills": 9, "experience": 7, "education": 8, "certifications": 3},
#     {"name": "Student_2", "skills": 6, "experience": 5, "education": 6, "certifications": 2},
#     {"name": "Student_3", "skills": 7, "experience": 4, "education": 5, "certifications": 1},
#     {"name": "Student_4", "skills": 8, "experience": 6, "education": 7, "certifications": 3},
#     {"name": "Student_5", "skills": 5, "experience": 5, "education": 6, "certifications": 4},
#     {"name": "Student_6", "skills": 4, "experience": 3, "education": 5, "certifications": 2},
#     {"name": "Student_7", "skills": 9, "experience": 7, "education": 8, "certifications": 5},
#     {"name": "Student_8", "skills": 3, "experience": 8, "education": 4, "certifications": 2},
#     {"name": "Student_9", "skills": 6, "experience": 5, "education": 5, "certifications": 1},
#     {"name": "Student_10", "skills": 8, "experience": 6, "education": 7, "certifications": 3},
# ]

# # Define employer weights for criteria
# employer_weights = {
#     "company_1": {"skills": 0.5, "experience": 0.2, "education": 0.1, "certifications": 0.2, "positions": 2},
#     "company_2": {"skills": 0.6, "experience": 0.3, "education": 0.05, "certifications": 0.05, "positions": 1},
#     "company_3": {"skills": 0.4, "experience": 0.4, "education": 0.1, "certifications": 0.1, "positions": 3},
#     "company_4": {"skills": 0.7, "experience": 0.2, "education": 0.05, "certifications": 0.05, "positions": 2},
#     "company_5": {"skills": 0.5, "experience": 0.25, "education": 0.15, "certifications": 0.1, "positions": 1},
#     "company_6": {"skills": 0.3, "experience": 0.4, "education": 0.25, "certifications": 0.05, "positions": 3},
#     "company_7": {"skills": 0.8, "experience": 0.1, "education": 0.05, "certifications": 0.05, "positions": 2},
#     "company_8": {"skills": 0.6, "experience": 0.3, "education": 0.05, "certifications": 0.05, "positions": 1},
#     "company_9": {"skills": 0.5, "experience": 0.3, "education": 0.1, "certifications": 0.1, "positions": 2},
#     "company_10": {"skills": 0.4, "experience": 0.4, "education": 0.15, "certifications": 0.05, "positions": 3},
# }

# # Instantiate the ranking system and generate employer rankings
# trial = StudentRankingSystem(students, employer_weights)
# employer_preference = trial.display_ranking()  # Use rank_students to get rankings for matching

# students_preference = {
#     "Student_1": ["company_1", "company_2", "company_3"],
#     "Student_2": ["company_2"],
#     "Student_3": ["company_5", "company_4", "company_3"],
#     "Student_4": ["company_1", "company_5", "company_6"],
#     "Student_5": ["company_6", "company_7", "company_8"],
#     "Student_6": ["company_4", "company_5", "company_9"],
#     "Student_7": ["company_2", "company_3", "company_7"],
#     "Student_8": ["company_1", "company_6", "company_10"],
#     "Student_9": ["company_3", "company_8", "company_9"],
#     "Student_10": ["company_2", "company_5", "company_6"],
# }

# # Perform the matching process
# match_trial = Matching(students_preference, employer_preference)
# best_match = match_trial.find_best_match()

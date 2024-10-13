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
            else:
                score += student[criterion] * weight
        return score  # Return as float for sorting

    def rank_students(self):
        # Dictionary to store rankings for each employer
        employer_rankings = {}
        
        # Loop over each employer and their weight criteria
        for employer, employer_weights in self.employers.items():
            student_scores = []  # Temporary list to store scores for the current employer
            
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
                
        return ranked_students



"""Handles Config"""


class Config:
    """App configuration settings"""

    def __init__(self):
        from app import DATABASE_MANAGER

        self.database_manager = DATABASE_MANAGER
        self.num_of_skills = 10
        self.min_num_ranking_student_to_opportunities = 5
        self.min_num_ranking_employer_to_students = 5

        self.update()

    def get_num_of_skills(self):
        """Get number of skills"""
        return self.num_of_skills

    def get_min_num_ranking_student_to_opportunities(self):

        return self.min_num_ranking_student_to_opportunities

    def get_min_num_ranking_employer_to_students(self):
        return self.min_num_ranking_employer_to_students

    def update(self):
        temp_num_of_skills = self.database_manager.get_one_by_field(
            "config", "name", "num_of_skills"
        )
        temp_min_num_ranking_student_to_opportunities = (
            self.database_manager.get_one_by_field(
                "config", "name", "min_num_ranking_student_to_opportunities"
            )
        )
        temp_min_num_ranking_employer_to_students = (
            self.database_manager.get_one_by_field(
                "config", "name", "min_num_ranking_employer_to_students"
            )
        )

        if temp_num_of_skills:
            self.num_of_skills = temp_num_of_skills["value"]

        if temp_min_num_ranking_student_to_opportunities:
            self.min_num_ranking_student_to_opportunities = (
                temp_min_num_ranking_student_to_opportunities["value"]
            )

        if temp_min_num_ranking_employer_to_students:
            self.min_num_ranking_employer_to_students = (
                temp_min_num_ranking_employer_to_students["value"]
            )

    def set_num_of_skills(self, num_of_skills):
        """Set number of skills"""
        self.database_manager.update_one_by_field(
            "config", "name", "num_of_skills", {"value": num_of_skills}
        )
        self.update()

    def set_min_num_ranking_student_to_opportunities(
        self, min_num_ranking_student_to_opportunities
    ):
        self.database_manager.update_one_by_field(
            "config",
            "name",
            "min_num_ranking_student_to_opportunities",
            {"value": min_num_ranking_student_to_opportunities},
        )
        self.update()

    def set_min_num_ranking_employer_to_students(
        self, min_num_ranking_employer_to_students
    ):
        self.database_manager.update_one_by_field(
            "config",
            "name",
            "min_num_ranking_employer_to_students",
            {"value": min_num_ranking_employer_to_students},
        )
        self.update()

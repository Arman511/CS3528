"""Handles Config"""


class Config:
    """App configuration settings"""

    def __init__(self):
        from app import DATABASE_MANAGER

        self.database_manager = DATABASE_MANAGER
        self.max_num_of_skills = 10
        self.min_num_ranking_student_to_opportunities = 5

        self.update()

    def get_max_num_of_skills(self) -> int:
        """Get number of skills"""
        return self.max_num_of_skills

    def get_min_num_ranking_student_to_opportunities(self) -> int:
        """Get minimum number of ranking student to opportunities"""
        return self.min_num_ranking_student_to_opportunities

    def update(self):
        temp_num_of_skills = self.database_manager.get_one_by_field(
            "config", "name", "num_of_skills"
        )
        temp_min_num_ranking_student_to_opportunities = (
            self.database_manager.get_one_by_field(
                "config", "name", "min_num_ranking_student_to_opportunities"
            )
        )

        if temp_num_of_skills:
            self.max_num_of_skills = temp_num_of_skills["value"]
        else:
            self.database_manager.insert(
                "config", {"name": "num_of_skills", "value": self.max_num_of_skills}
            )

        if temp_min_num_ranking_student_to_opportunities:
            self.min_num_ranking_student_to_opportunities = (
                temp_min_num_ranking_student_to_opportunities["value"]
            )
        else:
            self.database_manager.insert(
                "config",
                {
                    "name": "min_num_ranking_student_to_opportunities",
                    "value": self.min_num_ranking_student_to_opportunities,
                },
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

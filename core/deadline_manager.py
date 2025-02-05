"""
Handles connection to the MongoDB database and provides access to the collections.
"""

import datetime
from flask import jsonify


class DeadlineManager:
    def __init__(self):
        self.get_details_deadline()
        self.get_student_ranking_deadline()
        self.get_opportunities_ranking_deadline()

    def get_details_deadline(self):
        """Get the deadline from the database."""
        from app import DATABASE_MANAGER

        find_deadline = DATABASE_MANAGER.get_one_by_field("deadline", "type", 0)
        if not find_deadline:
            deadline = datetime.datetime.now().strftime("%Y-%m-%d")
            DATABASE_MANAGER.insert("deadline", {"type": 0, "deadline": deadline})
        else:
            deadline = find_deadline["deadline"]
        return deadline

    def is_past_details_deadline(self):
        """Check if the deadline has passed."""
        deadline = self.get_details_deadline()
        return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline

    def get_student_ranking_deadline(self):
        """Get the deadline from the database."""
        from app import DATABASE_MANAGER

        find_deadline = DATABASE_MANAGER.get_one_by_field("deadline", "type", 1)
        if not find_deadline:
            deadline = (
                datetime.datetime.strptime(self.get_details_deadline(), "%Y-%m-%d")
                + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
            DATABASE_MANAGER.insert("deadline", {"type": 1, "deadline": deadline})
        else:
            deadline = find_deadline["deadline"]
        return deadline

    def is_past_student_ranking_deadline(self):
        """Check if the deadline has passed."""
        deadline = self.get_student_ranking_deadline()
        return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline

    def get_opportunities_ranking_deadline(self):
        """Get the deadline from the database."""
        from app import DATABASE_MANAGER

        find_deadline = DATABASE_MANAGER.get_one_by_field("deadline", "type", 2)
        if not find_deadline:
            deadline = (
                datetime.datetime.strptime(
                    self.get_student_ranking_deadline(), "%Y-%m-%d"
                )
                + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
            DATABASE_MANAGER.insert("deadline", {"type": 2, "deadline": deadline})
        else:
            deadline = find_deadline["deadline"]
        return deadline

    def is_past_opportunities_ranking_deadline(self):
        """Check if the deadline has passed."""
        deadline = self.get_opportunities_ranking_deadline()
        return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline

    def update_deadlines(
        self, details_deadline, student_ranking_deadline, opportunities_ranking_deadline
    ):
        from app import DATABASE_MANAGER

        """Update the deadlines in the database."""

        try:
            datetime.datetime.strptime(details_deadline, "%Y-%m-%d")
            datetime.datetime.strptime(student_ranking_deadline, "%Y-%m-%d")
            datetime.datetime.strptime(opportunities_ranking_deadline, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid deadline format. Use YYYY-MM-DD."}), 400

        if details_deadline > student_ranking_deadline:
            return (
                jsonify(
                    {
                        "error": "Details deadline cannot be later than Student Ranking deadline."
                    }
                ),
                400,
            )
        if student_ranking_deadline > opportunities_ranking_deadline:
            return (
                jsonify(
                    {
                        "error": (
                            "Student Ranking deadline cannot be later than "
                            "Opportunities Ranking deadline."
                        )
                    }
                ),
                400,
            )
        if details_deadline > opportunities_ranking_deadline:
            return (
                jsonify(
                    {
                        "error": "Details deadline cannot be later than Opportunities Ranking deadline."
                    }
                ),
                400,
            )

        DATABASE_MANAGER.update_one_by_field(
            "deadline", "type", 0, {"deadline": details_deadline}
        )
        DATABASE_MANAGER.update_one_by_field(
            "deadline", "type", 1, {"deadline": student_ranking_deadline}
        )
        DATABASE_MANAGER.update_one_by_field(
            "deadline", "type", 2, {"deadline": opportunities_ranking_deadline}
        )

        return jsonify({"message": "All deadlines updated successfully"}), 200

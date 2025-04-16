"""
Handles connection to the MongoDB database and provides access to the collections.
"""

import datetime
from flask import jsonify, session


class DeadlineManager:
    """Handles deadlines for the application."""

    def __init__(self):
        from app import DATABASE_MANAGER

        self.database_manager = DATABASE_MANAGER
        details = self.get_details_deadline()
        student = self.get_student_ranking_deadline()
        opportunities = self.get_opportunities_ranking_deadline()
        if details > student or student > opportunities or details > opportunities:
            self.update_deadlines(
                details,
                (
                    datetime.datetime.strptime(details, "%Y-%m-%d")
                    + datetime.timedelta(weeks=1)
                ).strftime("%Y-%m-%d"),
                (
                    datetime.datetime.strptime(details, "%Y-%m-%d")
                    + datetime.timedelta(weeks=2)
                ).strftime("%Y-%m-%d"),
            )

    def get_details_deadline(self):
        """Get the deadline from the database."""

        find_deadline = self.database_manager.get_one_by_field("deadline", "type", 0)
        deadline = None
        if not find_deadline:
            deadline = (datetime.datetime.now() + datetime.timedelta(weeks=1)).strftime(
                "%Y-%m-%d"
            )
            self.database_manager.insert("deadline", {"type": 0, "deadline": deadline})
        else:
            deadline = find_deadline["deadline"]
        return deadline

    def is_past_details_deadline(self) -> bool:
        """Check if the deadline has passed."""
        deadline = self.get_details_deadline()
        return datetime.datetime.now() >= datetime.datetime.strptime(
            deadline, "%Y-%m-%d"
        )

    def get_student_ranking_deadline(self):
        """Get the deadline from the database."""

        find_deadline = self.database_manager.get_one_by_field("deadline", "type", 1)
        deadline = None
        if not find_deadline:
            deadline = (
                datetime.datetime.strptime(self.get_details_deadline(), "%Y-%m-%d")
                + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
            self.database_manager.insert("deadline", {"type": 1, "deadline": deadline})
        else:
            deadline = find_deadline["deadline"]
        return deadline

    def is_past_student_ranking_deadline(self) -> bool:
        """Check if the deadline has passed."""
        deadline = self.get_student_ranking_deadline()
        return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline

    def get_opportunities_ranking_deadline(self):
        """Get the deadline from the database."""

        find_deadline = self.database_manager.get_one_by_field("deadline", "type", 2)
        deadline = None
        if not find_deadline:
            deadline = (
                datetime.datetime.strptime(
                    self.get_student_ranking_deadline(), "%Y-%m-%d"
                )
                + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
            self.database_manager.insert("deadline", {"type": 2, "deadline": deadline})
        else:
            deadline = find_deadline["deadline"]
        return deadline

    def is_past_opportunities_ranking_deadline(self) -> bool:
        """Check if the deadline has passed."""
        deadline = self.get_opportunities_ranking_deadline()
        return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline

    def update_deadlines(
        self, details_deadline, student_ranking_deadline, opportunities_ranking_deadline
    ):
        """Update the deadlines in the database."""

        try:
            datetime.datetime.strptime(details_deadline, "%Y-%m-%d")
            datetime.datetime.strptime(student_ranking_deadline, "%Y-%m-%d")
            datetime.datetime.strptime(opportunities_ranking_deadline, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid deadline format. Use YYYY-MM-DD."}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

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

        self.database_manager.update_one_by_field(
            "deadline", "type", 0, {"deadline": details_deadline}
        )
        self.database_manager.update_one_by_field(
            "deadline", "type", 1, {"deadline": student_ranking_deadline}
        )
        self.database_manager.update_one_by_field(
            "deadline", "type", 2, {"deadline": opportunities_ranking_deadline}
        )

        return jsonify({"message": "All deadlines updated successfully"}), 200

    def get_deadline_type(self):

        if "employer" in session:
            pass

        if not self.is_past_details_deadline():
            return 0

        if not self.is_past_student_ranking_deadline():
            return 1

        if not self.is_past_opportunities_ranking_deadline() and session.get(
            "employer"
        ):
            employer_id = session["employer"]["_id"]
            opps = self.database_manager.get_all_by_field(
                "opportunities", "employer_id", employer_id
            )
            for opp in opps:
                if "preferences" not in opp:
                    return 2
            return 3

        elif not self.is_past_opportunities_ranking_deadline():
            return 3

        return None

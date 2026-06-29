from search.emails import send_results_email, send_no_results_email

class EmailNotificationService:
    def send_no_results(self, user_email: str, search_id: int, keywords: str):
        send_no_results_email(user_email=user_email, search_id=search_id, keywords=keywords)

    def send_results(self, user_email: str, courses: list[dict], search_id: int):
        send_results_email(user_email=user_email, courses=courses, search_id=search_id)
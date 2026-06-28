import os
import django 
from domain.exceptions import InvalidMessageError, SearchNotFoundError

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "optio.settings")
django.setup()

from search.models import Course, SearchRequest

class SearchRepository:
    def mark_search_status(self, search_id: int, status: str, results_count: int | None = None) -> None:
        search_request = SearchRequest.objects.filter(id=search_id).first()
        if not search_request:
            raise SearchRequest.DoesNotExist(f"SearchRequest {search_id} não encontrada.")

        update_fields = ["status"]
        search_request.status = status

        if results_count is not None:
            search_request.results_count = results_count
            update_fields.append("results_count")

        search_request.save(update_fields=update_fields)


    def save_courses(self, search_id: int, courses_data: list[dict]) -> int:
        search_request = SearchRequest.objects.get(id=search_id)
        course_objects = [
            Course(
                search_request=search_request,
                name=c["name"],
                institution=c["institution"],
                modality=c["modality"],
                state=c["state"],
                link=c["link"],
            )
            for c in courses_data
        ]
        Course.objects.bulk_create(course_objects)
        return len(course_objects)


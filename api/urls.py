from django.urls import path

from .stories import StoriesApi

urlpatterns = [
    path('projects/<int:project_id>/stories/<int:story_id>/', StoriesApi.as_view()),
    path('projects/<int:project_id>/stories/', StoriesApi.as_view())
]
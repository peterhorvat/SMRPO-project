from django.urls import path

from .stories import StoriesApi, StoriesConfirmApi

urlpatterns = [
    path('projects/<int:project_id>/stories/<int:story_id>/', StoriesApi.as_view()),
    path('projects/<int:project_id>/stories/', StoriesApi.as_view()),
    path('projects/<int:project_id>/stories/<int:story_id>/confirm', StoriesConfirmApi.as_view())
]
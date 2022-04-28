from django.urls import path

from .stories import StoriesApi, StoriesConfirmApi, StoriesRejectApi
from .posts import ProjectPosts, CommentPost

urlpatterns = [
    path('projects/<int:project_id>/stories/<int:story_id>/', StoriesApi.as_view()),
    path('projects/<int:project_id>/stories/', StoriesApi.as_view()),
    path('projects/<int:project_id>/stories/<int:story_id>/confirm/', StoriesConfirmApi.as_view()),
    path('projects/<int:project_id>/stories/<int:story_id>/reject/', StoriesRejectApi.as_view()),

    path('projects/<int:project_id>/posts/', ProjectPosts.as_view()),
    path('projects/<int:project_id>/addComment/<int:post_id>/', CommentPost.as_view())
]
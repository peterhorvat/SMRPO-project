"""Projekt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework import routers
from website import views as v

router = routers.DefaultRouter(trailing_slash=False)
# router.register(r'apiExample/$', v.viewExample, 'viewExample')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('404/', v.missing, name="not_dount"),
    path('', v.landing_page, name='landing_page'),
    path('login/', v.login_page, name='login_page'),
    path("create_new_project/", v.create_new_project, name='create_new_project'),
    path("delete_project/<int:id>", v.delete_project, name='delete_project'),
    path("projects/<int:project_id>/delete_sprint/<int:sprint_id>", v.delete_sprint, name='delete_sprint'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('createOTP/', v.createOTP, name='createOTP'),
    path('disableOTP/', v.disableOTP, name='disableOTP'),
    path('loginOTP/', v.loginOTP, name='loginOTP'),
    path('projects/<int:project_id>/create_sprint/', v.create_new_sprint, name='create_new_sprint'),
    path('projects/<int:project_id>/edit_sprint/<int:sprint_id>/', v.edit_sprint, name='edit_sprint'),
    path('projects/<int:project_id>/sprints/', v.sprint_list, name='sprint_list'),
    path('projects/<int:project_id>/', v.project_summary, name='project_summary'),
    path('projects/<int:project_id>/edit/', v.edit_project, name='edit_project_page'),
    path('projects/<int:project_id>/new_contributors', v.create_new_clan, name='new_contributors'),
    path('projects/<int:project_id>/product/', v.product_backlog, name='product_backlog'),
    path('projects/<int:project_id>/sprint_backlog/', v.sprint_backlog, name='sprint_backlog'),
    path('projects/<int:project_id>/add_new_member/', v.add_new_member, name='add_new_member'),
    path('projects/<int:project_id>/switch/', v.switch_roles, name='add_new_member'),
    path('projects/<int:project_id>/<int:member_id>/delete/', v.delete_member, name='delete_member'),
    path('user_settings/', v.update_user, name='update_user'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='change_password.html')),
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view(template_name='change_password_done.html'), name='password_change_done'),

    path("create_tasks/<int:story_id>/", v.create_new_task, name="create_new_task"),
    path("tasks_list/<int:story_id>/", v.tasks_list, name="tasks_list"),
    path("edit_tasks/<int:task_id>/", v.edit_task, name="edit_task"),
    path("accept_task/<int:task_id>/", v.accept_task, name="accept_task"),
    path("resign_task/<int:task_id>/", v.resign_task, name="resign_task"),
    path("start_task/<int:task_id>/", v.start_task, name="start_task"),
    path("finish_task/<int:task_id>/", v.finish_task, name="finish_task"),
    path('task/<int:pk>/edit', v.edit_task, name='edit_task'),
    path('task/<int:pk>/remove', v.remove_task, name='remove_task'),

    path('stories_to_sprint/<int:project_id>/<int:sprint_id>/', v.stories_to_sprint, name='stories_to_sprint'),

    path('api/', include('api.urls'), name='API'),
]

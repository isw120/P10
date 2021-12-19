"""SoftDesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from .views import SignupAPIView, ProjectsAPIView, ContributorsAPIView, IssuesAPIView, CommentsAPIView

urlpatterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('projects/', ProjectsAPIView.as_view(), name='projects'),
    path('projects/<project_id>', ProjectsAPIView.as_view(), name='projects'),
    path('projects/<project_id>/users/', ContributorsAPIView.as_view(), name='contributors'),
    path('projects/<project_id>/users/<contributor_id>', ContributorsAPIView.as_view(), name='contributors'),
    path('projects/<project_id>/issues/', IssuesAPIView.as_view(), name='issues'),
    path('projects/<project_id>/issues/<issue_id>', IssuesAPIView.as_view(), name='issues'),
    path('projects/<project_id>/issues/<issue_id>/comments/', CommentsAPIView.as_view(), name='comments'),
    path('projects/<project_id>/issues/<issue_id>/comments/<comment_id>', CommentsAPIView.as_view(), name='comments'),
]

from django.urls import path
from . import views

urlpatterns = [
    # Opinions
    path('', views.OpinionListView.as_view(), name='opinion-list'),
    path('opinions/create/', views.OpinionCreateView.as_view(), name='opinion-create'),
    path('opinions/<int:pk>/', views.OpinionDetailView.as_view(), name='opinion-detail'),

    path('opinions/<int:pk>/update/', views.OpinionUpdateView.as_view(), name='opinion-update'),
    path('opinions/<int:pk>/delete/', views.OpinionDeleteView.as_view(), name='opinion-delete'),

    # Arguments
    path('opinions/<int:pk>/argue/', views.ArgumentCreateView.as_view(), name='argument-create'),
    path('arguments/<int:pk>/delete/', views.ArgumentDeleteView.as_view(), name='argument-delete'),

    # Tags
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    path('tags/create/', views.TagCreateView.as_view(), name='tag-create'),

    # Profile
    path('profile/<str:username>/', views.ProfileView.as_view(), name='profile'),
]
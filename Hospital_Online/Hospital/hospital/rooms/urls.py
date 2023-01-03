from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from . import views


router = routers.DefaultRouter()
router.register(prefix='categories', viewset=views.CategoryViewset, basename='category')
router.register(prefix='khoa', viewset=views.KhoaViewSet, basename='khoa')
router.register(prefix='rooms', viewset=views.RoomViewSet, basename='room')
router.register(prefix='comments', viewset=views.CommentViewSet, basename='comment')
router.register(prefix='users', viewset=views.UserViewSet, basename='user')


urlpatterns = [
    path('', include(router.urls)),
    path('my-khoa/', views.MyCourseView.as_view()),
    path('oauth2-info/', views.AuthInfo.as_view()),
    path('my-khoa/<int:pk>/', views.MyCourseDetailView.as_view())
]
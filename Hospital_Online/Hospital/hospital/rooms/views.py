from typing import List, Any

from rest_framework import viewsets, generics, status, permissions, mixins
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Khoa, Room, Comment, User, Like, Rating, RoomView
from .serializers import (
    CategorySerializer, KhoaSerializer,
    RoomSerializer, RoomDetailSerializer,
    AuthRoomDetailSerializer,
    CommentSerializer, CreateCommentSerializer,
    UserSerializer,
    RoomViewSerializer
)
from .paginators import KhoaPaginator
from drf_yasg.utils import swagger_auto_schema
from .perms import CommentOwnerPerms
from django.db.models import F
from django.conf import settings


class CategoryViewset(viewsets.ViewSet, generics.ListAPIView):
    queryset = Category.objects.filter(active=True)
    serializer_class = CategorySerializer

    def get_queryset(self):
        q = self.queryset

        kw = self.request.query_params.get('kw')
        if kw:
            q = q.filter(name__icontains=kw)

        return q


class KhoaViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Khoa.objects.filter(active=True)
    serializer_class = KhoaSerializer
    pagination_class = KhoaPaginator

    def get_queryset(self):
        queryset = self.queryset

        kw = self.request.query_params.get("kw")
        if kw:
            queryset = queryset.filter(subject__icontains=kw)

        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset

    @swagger_auto_schema(
        operation_description='Get the room of a hospital',
        responses={
            status.HTTP_200_OK: RoomSerializer()
        }
    )
    @action(methods=['get'], detail=True, url_path='rooms')
    def get_rooms(self, request, pk):
        # khoa = Khoa.objects.get(pk=pk)
        khoa = self.get_object()
        rooms = khoa.rooms.filter(active=True)

        kw = request.query_params.get('kw')
        if kw:
            rooms = rooms.filter(subject__icontains=kw)

        return Response(data=RoomSerializer(rooms, many=True, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class RoomViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Room.objects.filter(active=True)
    serializer_class = RoomDetailSerializer

    def get_serializer_class(self):
        if self.request.user.is_authenticated:
            return AuthRoomDetailSerializer

        return RoomDetailSerializer

    def get_permissions(self):
        if self.action in ['like', 'rating', 'comments']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @swagger_auto_schema(
        operation_description='Get the comments of a room',
        responses={
            status.HTTP_200_OK: CommentSerializer()
        }
    )
    @action(methods=['post'], url_path='comments', detail=True)
    def comments(self, request, pk):
        room = self.get_object()
        comments = room.comments.select_related('user').filter(active=True)

        return Response(CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='like', detail=True)
    def like(self, request, pk):
        room = self.get_object()
        user = request.user

        l, _ = Like.objects.get_or_create(room=room, user=user)
        l.active = not l.active
        try:
            l.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=AuthRoomDetailSerializer(room, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(methods=['post'], url_path='rating', detail=True)
    def rating(self, request, pk):
        room = self.get_object()
        user = request.user
        rating = int(request.data['rating'])

        r, _ = Rating.objects.get_or_create(room=room, user=user, defaults={"rate": rating})
        r.rate = request.data.get('rate', 0)
        try:
            r.save()
        except:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data=AuthRoomDetailSerializer(room, context={'request': request}).data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='views')
    def inc_view(self, request, pk):
        v, created = RoomView.objects.get_or_create(room=self.get_object())
        v.views = F('views') + 1
        v.save()
        v.refresh_from_db()
        return Response(RoomViewSerializer(v).data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ViewSet, generics.CreateAPIView,
                     generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = Comment.objects.filter(active=True)
    serializer_class = CreateCommentSerializer
    permission_classes = [permissions.AllowAny()]

    def get_permissions(self):
        if self.action in ['update', 'destroy']:
            return [CommentOwnerPerms()]

        return [permissions.AllowAny()]


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]

    def get_permissions(self):
        if self.action == 'current_user':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], url_path="current-user", detail=False)
    def current_user(self, request):
        return Response(self.serializer_class(request.user, context={'request': request}).data,
                        status=status.HTTP_200_OK)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)


class MyCourseView(generics.ListCreateAPIView):
    lookup_field = ['subject']
    queryset = Khoa.objects.filter(active=True)
    serializer_class = KhoaSerializer


class MyCourseDetailView(generics.RetrieveAPIView):
    queryset = Khoa.objects.filter(active=True)
    serializer_class = KhoaSerializer
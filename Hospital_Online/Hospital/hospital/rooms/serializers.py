from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Category, Khoa, Room, Tag, Comment, User, RoomView


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class KhoaSerializer(ModelSerializer):
    image = SerializerMethodField(source='image')

    def get_image(self, obj):
        request = self.context['request']
        # if obj.image and obj.image.name.startswith("/static"):
        #     pass
        # else:
        path = '/static/%s' % obj.image.name

        return request.build_absolute_uri(path)

    class Meta:
        model = Khoa
        fields = ['id', 'subject', 'created_date', 'image', 'category_id']


class TagSeriazlier(ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class RoomSerializer(ModelSerializer):
    image = SerializerMethodField(source='image')
    tags = TagSeriazlier(many=True)

    def get_image(self, obj):
        request = self.context['request']
        # if obj.image and obj.image.name.startswith("/static"):
        #     pass
        # else:
        path = '/static/%s' % obj.image.name

        return request.build_absolute_uri(path)

    class Meta:
        model = Room
        fields = ['id', 'subject', 'created_date', 'updated_date', 'khoa_id', 'image', 'tags']


class RoomDetailSerializer(RoomSerializer):
    rate = SerializerMethodField()

    def get_rate(self, room):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            r = room.rating_set.filter(user=request.user).first()
            if r:
                return r.rate
        return -1

    class Meta:
        model = Room
        fields = RoomSerializer.Meta.fields + ['content', 'rate']


class AuthRoomDetailSerializer(RoomDetailSerializer):
    like = SerializerMethodField()
    rating = SerializerMethodField()

    def get_like(self, room):
        request = self.context.get('request')
        if request:
            return room.like_set.filter(user=request.user, active=True).exists()

    def get_rating(self, room):
        request = self.context.get('request')
        if request:
            r = room.rating_set.filter(user=request.user).first()
            if r:
                return r.rate

    class Meta:
        model = Room
        fields = RoomDetailSerializer.Meta.fields + ['like', 'rating']


class UserSerializer(ModelSerializer):
    avatar = SerializerMethodField(source='avatar')

    def get_avatar(self, obj):
        request = self.context['request']
        if obj.avatar and not obj.avatar.name.startswith("/static"):

            path = '/static/%s' % obj.avatar.name

            return request.build_absolute_uri(path)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name',
                  'username', 'password', 'email',
                  'avatar']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        data = validated_data.copy()
        user = User(**data)
        user.set_password(user.password)
        user.save()

        return user


class CreateCommentSerializer(ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'user', 'room', 'created_date', 'updated_date']


class CommentSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Comment
        exclude = ['active']


class RoomViewSerializer(ModelSerializer):
    class Meta:
        model = RoomView
        fields = ["id", "views", "room"]
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField


class User(AbstractUser):
    avatar = models.ImageField(null=True, upload_to='users/%Y/%m')


class ModelBase(models.Model):
    active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CVOnline(ModelBase):
    intro = RichTextField()
    from_salary = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    to_salary = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)


class Category(ModelBase):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Khoa(ModelBase):
    subject = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='Khoa/%Y/%m')
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    pre_khoa = models.ManyToManyField('self', null=True, symmetrical=False)

    def __str__(self):
        return self.subject

    class Meta:
        unique_together = ('subject', 'category')


class Room(ModelBase):
    subject = models.CharField(max_length=255)
    content = RichTextField()
    image = models.ImageField(null=True, upload_to='Rooms/%Y/%m')
    khoa = models.ForeignKey(Khoa,
                               related_name='rooms',
                               related_query_name='my_room',
                               on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    viewers = models.ManyToManyField(User, through='UserRoomView')

    class Meta:
        unique_together = ('subject', 'khoa')

    def __str__(self):
        return self.subject


class UserRoomView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    counter = models.IntegerField(default=0)
    reading_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'room')


class Comment(ModelBase):
    content = models.TextField()
    room = models.ForeignKey(Room,
                               related_name='comments',
                               on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class Tag(ModelBase):
    name = models.CharField(max_length=50, unique=True, null=True)

    def __str__(self):
        return self.name


class ActionBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'room')
        abstract = True


class Like(ActionBase):
    active = models.BooleanField(default=False)
    LIKE, HAHA, HEART = range(3)
    ACTIONS = [
        (LIKE, 'like'),
        (HAHA, 'haha'),
        (HEART, 'heart')
    ]
    type = models.PositiveSmallIntegerField(choices=ACTIONS, default=LIKE)


class Rating(ActionBase):
    rate = models.SmallIntegerField(default=1)


class RoomView(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)
    room = models.OneToOneField(Room, on_delete=models.CASCADE)
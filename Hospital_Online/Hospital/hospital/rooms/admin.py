from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from .models import Category, Khoa, User, Room, Comment, Tag
from django.utils.html import mark_safe
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.urls import path


class RoomForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorUploadingWidget)

    class Meta:
        model = Room
        fields = '__all__'


class KhoaAdmin(admin.ModelAdmin):
    search_fields = ['subject', 'category']
    readonly_fields = ['image_view']

    def image_view(self, khoa):
        if khoa:
            return mark_safe(
                '<img src="/static/{url}" width="120" />' \
                    .format(url=khoa.image.name)
            )

    def get_urls(self):
        return [
           path('khoa-stats/', self.stats_view)
        ] + super().get_urls()


    def stats_view(self, request):
        c = Khoa.objects.filter(active=True).count()
        stats = Khoa.objects.annotate(room_count=Count('my_room')).values('id', 'subject', 'room_count')

        return TemplateResponse(request,
                                'admin/khoa-stats.html', {
                                    'count': c,
                                    'stats': stats
                                })




class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ['name', 'created_date']
    list_display = ['id', 'name', 'created_date']


class RoomTagInlineAdmin(admin.TabularInline):
    model = Room.tags.through


class TagAdmin(admin.ModelAdmin):
    inlines = [RoomTagInlineAdmin, ]


class RoomAdmin(admin.ModelAdmin):
    form = RoomForm
    inlines = [RoomTagInlineAdmin, ]


# Register your models here.
admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Khoa, KhoaAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Tag)
admin.site.register(Comment)
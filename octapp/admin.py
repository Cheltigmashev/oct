from django.contrib import admin
from .models import Test, Comment, Category, ResultScale, Tag

admin.site.register(Test)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(ResultScale)
admin.site.register(Tag)

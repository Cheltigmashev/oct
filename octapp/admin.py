from django.contrib import admin
from .models import Test, Comment, Category, ResultScale, Tag, Test_rate
from .models import ClosedQuestion, ClosedQuestionOption, OpenQuestion, SequenceQuestion
from .models import SequenceQuestionElement, ComparisonQuestion, ComparisonQuestionElement

admin.site.register(Test)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(ResultScale)
admin.site.register(Tag)
admin.site.register(Test_rate)

admin.site.register(ClosedQuestion)
admin.site.register(ClosedQuestionOption)
admin.site.register(OpenQuestion)
admin.site.register(SequenceQuestion)
admin.site.register(SequenceQuestionElement)
admin.site.register(ComparisonQuestion)
admin.site.register(ComparisonQuestionElement)

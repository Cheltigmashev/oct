from .models import Test, Category, Tag

def footer_statistics_processor(request):
    return {'all_tests_count': Test.objects.count(),
            'all_categories_count': Category.objects.count(),
            'all_tags_count': Tag.objects.count()}

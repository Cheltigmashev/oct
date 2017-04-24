from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TestForm
from .models import Test, Comment, Test_rate, Tag, Category
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
import re

# Модель пользователя
User = get_user_model()

def get_tests_lists_context():
    showing_tests_per_one_column = 14
    showing_tags_and_categories_amount = 58
    showing_tags = Tag.objects.order_by('pk')[:showing_tags_and_categories_amount]
    showing_categories = Category.objects.filter(confirmed=True).order_by('pk')[:showing_tags_and_categories_amount]

    # левый ряд тестов для списка новых тестов, диапазон от 0го до showing_tests_per_one_column - 1
    left_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date', 'name')[:showing_tests_per_one_column]
    # левый ряд тестов для списка новых тестов
    right_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date', 'name')[showing_tests_per_one_column:showing_tests_per_one_column*2]
    # левый ряд тестов для списка рейтинговых тестов, диапазон от 0го до showing_tests_per_one_column - 1
    left_number_of_popular_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[:showing_tests_per_one_column]
    # левый ряд тестов для списка рейтинговых тестов
    right_number_of_popular_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[showing_tests_per_one_column:showing_tests_per_one_column*2]
    
    all_tags_count = Tag.objects.order_by('pk').count()
    all_published_test_count = Test.objects.filter(published_date__isnull=False).count()
    all_confirmed_categories_count = Category.objects.filter(confirmed=True).count()
    
    if all_tags_count > showing_tags_and_categories_amount:
        show_elision_marks_for_tags = True
    else:
        show_elision_marks_for_tags = None
    if all_confirmed_categories_count > showing_tags_and_categories_amount:
        show_elision_marks_for_categories = True
    else:
        show_elision_marks_for_categories = None
    if all_published_test_count > left_number_of_new_tests_list.count() + right_number_of_new_tests_list.count():
        show_elision_marks_for_tests = True
    else:
        show_elision_marks_for_tests = None

    unconfirmed_categories = Category.objects.filter(confirmed=False)
    count_of_tests_without_category = Test.objects.filter(category=None).count()
    count_of_tests_with_unconf_cat = 0
    for unconf_cat in unconfirmed_categories:
        count_of_tests_with_unconf_cat += unconf_cat.tests.count()
    tests_lists_context = {'left_number_of_new_tests_list': left_number_of_new_tests_list,
                           'right_number_of_new_tests_list': right_number_of_new_tests_list,
                           'left_number_of_popular_tests': left_number_of_popular_tests,
                           'right_number_of_popular_tests': right_number_of_popular_tests,
                           'showing_tags': showing_tags,
                           'showing_categories': showing_categories,
                           'count_of_tests_with_unconf_cat': count_of_tests_with_unconf_cat,
                           'show_elision_marks_for_tags': show_elision_marks_for_tags,
                           'show_elision_marks_for_categories': show_elision_marks_for_categories,
                           'show_elision_marks_for_tests': show_elision_marks_for_tests,
                           'count_of_tests_without_category': count_of_tests_without_category}
    return tests_lists_context

# Представление главной страницы
def tests_lists(request):
    return render(request, 'octapp/tests_lists.html', get_tests_lists_context())

@login_required
def user_tests(request, pk):
    published_user_tests = Test.objects.filter(author=request.user).order_by('name').filter(published_date__isnull=False)
    unpublished_user_tests = Test.objects.filter(author=request.user).order_by('name').filter(published_date__isnull=True)
    return render(request, 'octapp/user_tests.html', {'unpublished_user_tests': unpublished_user_tests,
            'published_user_tests': published_user_tests})

@login_required
def test_new(request):
    if request.method == "POST":
        # Form форма с пользовательскими данными
        form = TestForm(request.POST)
        if form.is_valid():
            # Если использовать form.save(Commit=False), то выбранные пользователем теги к тесту не добавляются!
            # Это происходит потому невозможно создать связи для объекта, который не сохранен в базе данных.
            # Подробнее см. https://djbook.ru/rel1.9/topics/forms/modelforms.html#the-save-method
            test = form.save()
            test.author = request.user
            test.name = test.name.capitalize()
            stripped_category_name = form.cleaned_data['new_category'].strip(' ')
            # Если пользователь выберет какую-либо категорию и, при этом, введет новую, то новая добавляться не будет,
            # а тесту присвоится выбранная им категория
            if form.cleaned_data['new_category'] and not form.cleaned_data['category']:
                if not Category.objects.filter(name__iexact=stripped_category_name):
                    test.category = Category.objects.create(name=form.cleaned_data['new_category'].capitalize())
                else:
                    test.category = Category.objects.get(name__iexact=stripped_category_name)
            if form.cleaned_data['new_tags']:
                pattern = r'[\w/\-\d ]+'
                new_tags = re.findall(pattern, form.cleaned_data['new_tags'])
                for item in new_tags:
                    # Если такого тега еще нет в базе
                    if not Tag.objects.filter(name__iexact=item):
                        new_tag_object = Tag.objects.create(name=item)
                        test.tags.add(new_tag_object)
                    # Если такой тег уже есть в базе
                    else:
                        test.tags.add(Tag.objects.get(name__iexact=item))
            if form.cleaned_data['publish_after_adding']:
                test.published_date = timezone.now()
            test.save()
            return redirect('test_detail', pk=test.pk)
    else:
        # Пустая форма
        form = TestForm()
    return render(request, 'octapp/test_edit.html', {'form': form})

def test_detail(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.user == test.author:
        is_author = True
    else:
        is_author = False
    if not request.user.is_authenticated:
        return render(request, 'octapp/test_detail.html', {'test': test })
    else:
        try:
            rate_of_current_user = Test_rate.objects.get(test=test, reviewer=request.user)
            return render(request, 'octapp/test_detail.html', {'test': test, 'is_author': is_author, 'rate_of_current_user': rate_of_current_user })
        # Пользователь еще не ставил оценку данному тесту
        except Test_rate.DoesNotExist:
            return render(request, 'octapp/test_detail.html', {'test': test, 'is_author': is_author })

@login_required
def test_edit(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == "POST":
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            test = form.save()
            return redirect('test_detail', pk=test.pk)
    else:
        form = TestForm(instance=test)
    return render(request, 'octapp/test_edit.html', {'form': form, 'test': test})

@login_required
def test_publish(request, pk, through_user_tests):
    test = get_object_or_404(Test, pk=pk)
    test.publish()
    if through_user_tests == 'True':
        return redirect('user_tests', pk=pk)
    else:
        return redirect('test_detail', pk=pk)

@login_required
def test_unpublish(request, pk, through_user_tests):
    test = get_object_or_404(Test, pk=pk)
    test.unpublish()
    if through_user_tests == 'True':
        return redirect('user_tests', pk=pk)
    else:
        return redirect('test_detail', pk=pk)

@login_required
def test_make_ready_for_passing(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.make_ready_for_passing()
    return redirect('test_detail', pk=pk)

@login_required
def test_remove(request, pk, through_user_tests):
    test = get_object_or_404(Test, pk=pk)
    test.delete()
    if through_user_tests == 'True':
        return redirect('user_tests', pk=pk)
    else:
        return redirect('tests_lists')

@login_required
def review(request, test_id, user_rate):
    test = get_object_or_404(Test, pk=test_id)
    user = request.user
    # Устранение возможности голосовать за других пользователей с помощью ввода URL
    if user == request.user:
        if user_rate == "like":
            bool_rate = True
        elif user_rate == "dislike":
            bool_rate = False
        # Пользователь еще не ставил оценку данному тесту
        if not test.rates.filter(reviewer=user):
            # Создаем новый объект модели Test_rate для данного пользователя, теста и оценки, а также
            # добавляем его в связанные объекты объекта Test
            test_rate = Test_rate(test=test, reviewer=user, like=bool_rate)
            test_rate.save(force_insert=True)
            if user_rate == "like":
                test.review_positively()
            else:
                test.review_negatively() 
            return redirect('test_detail', pk=test_id)
        else:
            return redirect('tests_lists')            
    else:
        return redirect('user_tests')

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    test_pk = comment.test.pk
    comment.delete()
    return redirect('test_detail', pk=test_pk)

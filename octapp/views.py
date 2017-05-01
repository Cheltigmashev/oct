from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TestForm
from .models import Test, Comment, Test_rate, Tag, Category
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
import re

# Модель пользователя
User = get_user_model()

def get_tests_lists_context():
    showing_tests_per_one_column = 14
    showing_tags_and_categories_amount = 58

    # левый ряд тестов для списка новых тестов, диапазон от 0го до showing_tests_per_one_column - 1
    left_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date', 'name')[:showing_tests_per_one_column]
    # левый ряд тестов для списка новых тестов
    right_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date', 'name')[showing_tests_per_one_column:showing_tests_per_one_column*2]
    # левый ряд тестов для списка рейтинговых тестов, диапазон от 0го до showing_tests_per_one_column - 1
    left_number_of_rating_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[:showing_tests_per_one_column]
    # левый ряд тестов для списка рейтинговых тестов
    right_number_of_rating_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[showing_tests_per_one_column:showing_tests_per_one_column*2]
    
    showing_tags_and_count_of_published_tests = []
    for tag in Tag.objects.order_by('-pk')[:showing_tags_and_categories_amount]:
        showing_tags_and_count_of_published_tests.append([tag, tag.tests.filter(published_date__lte=timezone.now()).count()])        

    showing_categories_and_count_of_published_tests = []
    for category in Category.objects.filter(confirmed=True).order_by('-pk')[:showing_tags_and_categories_amount]:
        showing_categories_and_count_of_published_tests.append([category, category.tests.filter(published_date__lte=timezone.now()).count()])        

    all_tags_count = Tag.objects.count()
    
    all_published_test_count = Test.objects.filter(published_date__lte=timezone.now()).count()
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

    count_of_tests_without_category = Test.objects.filter(category=None).filter(published_date__lte=timezone.now()).count()
    count_of_tests_without_tags = Test.objects.filter(tags=None).filter(published_date__lte=timezone.now()).count()

    count_of_published_tests_with_unconf_cat = 0
    for unconf_cat in unconfirmed_categories:
        count_of_published_tests_with_unconf_cat += unconf_cat.tests.filter(published_date__lte=timezone.now()).count()

    tests_lists_context = {'left_number_of_new_tests_list': left_number_of_new_tests_list,
                           'right_number_of_new_tests_list': right_number_of_new_tests_list,
                           'left_number_of_rating_tests': left_number_of_rating_tests,
                           'right_number_of_rating_tests': right_number_of_rating_tests,
                           'showing_tags_and_count_of_published_tests': showing_tags_and_count_of_published_tests,
                           'showing_categories_and_count_of_published_tests': showing_categories_and_count_of_published_tests,
                           'count_of_published_tests_with_unconf_cat': count_of_published_tests_with_unconf_cat,
                           'show_elision_marks_for_tags': show_elision_marks_for_tags,
                           'show_elision_marks_for_categories': show_elision_marks_for_categories,
                           'show_elision_marks_for_tests': show_elision_marks_for_tests,
                           'count_of_tests_without_category': count_of_tests_without_category,
                           'count_of_tests_without_tags': count_of_tests_without_tags}
    return tests_lists_context

# Получает данные и возвращает контекст, связанный с постраничным выводом
def get_pagination(page, some_page, on_one_page, max_pages_before_or_after_current):
    paginator = Paginator(some_page, on_one_page)
    try:
        some_page = paginator.page(page)
    except PageNotAnInteger:
        some_page = paginator.page(1)
    except EmptyPage:
        some_page = paginator.page(paginator.num_pages)
    # Все страницы меньше текущей будут отображены
    if page - max_pages_before_or_after_current <= 1:
        # Диапазон номеров страниц, которые меньше текущей
        pages_before_current = range(1, paginator.num_pages if page > paginator.num_pages else page)
        previous = None
    # Не все страницы меньше текущей будут отображены
    else:
        pages_before_current = range(page - max_pages_before_or_after_current, paginator.num_pages if page > paginator.num_pages else page)
        previous = pages_before_current[0] - 1
    # Если правый отображаемый диапазон номеров страниц выходит за границы возможных номеров
    if page + max_pages_before_or_after_current >= paginator.num_pages:
        # Диапазон номеров страниц, которые больше текущей        
        pages_after_current = range(page + 1, paginator.num_pages + 1)
        next = None
    else:
        pages_after_current = range(page + 1, page + max_pages_before_or_after_current + 1)
        next = pages_after_current[-1] + 1
    context = {'pages_before_current': pages_before_current,
            'pages_after_current': pages_after_current,
            'previous': previous,
            'next': next,
            'some_page': some_page}
    return context

# Представление главной страницы
def tests_lists(request):
    return render(request, 'octapp/tests_lists.html', get_tests_lists_context())

def get_filtered_and_sorted_tests_with_pagination(request, tests):
    q_dict = request.GET.dict()
    context = { }
    if request.GET.get('selected_category', '') == 'null':
        # Отбираем тесты без категории
        tests = tests.filter(category__isnull=True).order_by('name')
        context['selected_category'] = 'null'
    elif request.GET.get('selected_category', '') == 'unconfirmed':
        # Отбираем тесты с неподтвержденной категорией
        tests = tests.filter(category__confirmed=False).order_by('name')
        context['selected_category'] = 'unconfirmed'
    elif request.GET.get('selected_category', '') == 'any':
        context['selected_category'] = 'any'
    elif 'selected_category' in request.GET:
        selected_category_object = get_object_or_404(Category, pk=int(request.GET.get('selected_category')))
        # Отбираем тесты с определенной категорией
        tests = tests.filter(category=selected_category_object)
        context['selected_category'] = request.GET.get('selected_category')
        context['selected_category_object'] = selected_category_object

    if request.GET.get('selected_tag', '') == 'null':
        # Отбираем тесты без тегов
        tests = tests.filter(tags__isnull=True)
        context['selected_tag'] = 'null'
    elif request.GET.get('selected_tag', '') == 'any':
        # Отбираем тесты с любыми тегами
        context['selected_tag'] = 'any'
    elif 'selected_tag' in request.GET:
        selected_tag_object = get_object_or_404(Tag, pk=int(request.GET.get('selected_tag')))
        # Отбираем тесты с определенным тегом
        tests = tests.filter(tags=selected_tag_object)
        context['selected_tag'] = request.GET.get('selected_tag')
        context['selected_tag_object'] = selected_tag_object

    if request.GET.get('sorting', '') == 'rating_desc':
        tests = tests.order_by('-rating', 'name')
        context['sorting'] = 'rating_desc'
    elif request.GET.get('sorting', '') == 'published_date_desc':
        tests = tests.order_by('-published_date')
        context['sorting'] = 'published_date_desc'
    elif request.GET.get('sorting', '') == 'name_asc':
        tests = tests.order_by('name')
        context['sorting'] = 'name_asc'

    if request.GET.get('filter_ready_for_passing', '') == 'on':
        tests = tests.filter(ready_for_passing=True)
        context['filter_ready_for_passing'] = 'on'
    elif request.GET.get('filter_time_restriction', '') == 'on':
        tests = tests.filter(time_restricting__isnull=False)
        context['filter_time_restriction'] = 'on'
    elif request.GET.get('filter_passing_control', '') == 'on':
        tests = tests.filter(controlling=True)
        context['filter_passing_control'] = 'on'

    # По-хорошему, в случае использования функции для представления tests,
    # этот код не нужен. Он используется только для представления user_tests
    if request.GET.get('publish_status', '') == 'published':
        tests = tests.filter(published_date__lte=timezone.now())
        context['publish_status'] = 'published'
    elif request.GET.get('publish_status', '') == 'unpublished':
        tests = tests.filter(published_date__isnull=True)
        context['publish_status'] = 'unpublished'
    elif request.GET.get('publish_status', '') == 'any':
        context['publish_status'] = 'any'
    # Если этого HTTP-параметра вообще нет в запросе,
    # то в tests все еще будут как опубликованные, так и неопубликованные тесты 

    page = request.GET.get('page', '1')
    page = int(page)
    # 35, 5 prod
    pag_context = get_pagination(page, tests, 35, 5)
    context.update(pag_context)

    categories_for_filtering_of_tests = Category.objects.filter(confirmed=True).order_by('name')
    tags_for_filtering_of_tests = Tag.objects.order_by('name')
    context.update({'categories_for_filtering_of_tests': categories_for_filtering_of_tests, 'tags_for_filtering_of_tests': tags_for_filtering_of_tests})

    q = QueryDict(mutable=True)
    # В навигационных ссылках добавляется &page=X, поэтому если в запросе уже есть page, 
    # добавленный после перехода по страницам, то нужно его удалить
    if 'page' in q_dict:
        q_dict.pop('page')
    q.update(q_dict)
    context['HTTPparameters'] = '?' + q.urlencode()
    return context

def get_categories_with_count_of_published_tests(context, categories):
    # Нужно изменить количество тестов, выводимых при фильтрации по категории
    categories_and_count_of_published_tests_in_them = []
    for category in categories:
        categories_and_count_of_published_tests_in_them.append([category, category.tests.filter(published_date__lte=timezone.now()).count])
    context['categories_and_count_of_published_tests_in_them'] = categories_and_count_of_published_tests_in_them
    return context

def get_tags_with_count_of_published_tests(context, tags):
    # Нужно изменить количество тестов, выводимых при фильтрации по тегу
    tags_and_count_of_published_tests_in_them = []
    for tag in tags:
        tags_and_count_of_published_tests_in_them.append([tag, tag.tests.filter(published_date__lte=timezone.now()).count])
    context['tags_and_count_of_published_tests_in_them'] = tags_and_count_of_published_tests_in_them
    return context

# 3 списка тестов (№ 2, № 3, № 4), на которые можно перейти из главной страницы
def tests(request):
    # Если сортировка не задана, то тесты будут по алфавиту
    tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('name')
    context = get_filtered_and_sorted_tests_with_pagination(request, tests)
    context = get_categories_with_count_of_published_tests(context, context['categories_for_filtering_of_tests'])
    context = get_tags_with_count_of_published_tests(context, context['tags_for_filtering_of_tests'])
    return render(request, 'octapp/tests.html', context)

def categories(request):
    categories = Category.objects.filter(confirmed=True).order_by('name')
    context = get_pagination(int(request.GET.get('page', '1')), categories, 45, 5)
    context = get_categories_with_count_of_published_tests(context, categories)
    return render(request, 'octapp/categories.html', context)

def tags(request):
    tags = Tag.objects.order_by('name')
    context = get_pagination(int(request.GET.get('page', '1')), tags, 45, 5)
    context.update(get_tags_with_count_of_published_tests(context, tags))
    return render(request, 'octapp/tags.html', context)

@login_required
def user_tests(request, pk):
    user_tests = Test.objects.filter(author=request.user).order_by('name')
    context = get_filtered_and_sorted_tests_with_pagination(request, user_tests)
    # Нужно изменить количество тестов, выводимых при фильтрации по категории или по тегу
    categories_and_count_of_user_tests_in_them = []
    tags_and_count_of_user_tests_in_them = []
    for category in context['categories_for_filtering_of_tests']:
        categories_and_count_of_user_tests_in_them.append([category, category.tests.filter(author=request.user).count()])
    for tag in context['tags_for_filtering_of_tests']:
        tags_and_count_of_user_tests_in_them.append([tag, tag.tests.filter(author=request.user).count()])
    context['categories_and_count_of_user_tests_in_them'] = categories_and_count_of_user_tests_in_them
    context['tags_and_count_of_user_tests_in_them'] = tags_and_count_of_user_tests_in_them
    return render(request, 'octapp/user_tests.html', context)

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
    #test = get_object_or_404(Test, pk=pk, pub_date__lte=timezone.now())
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

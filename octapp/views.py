from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TestForm, ClosedQuestionForm, OpenQuestionForm, SequenceQuestionForm, ComparisonQuestionForm, ClosedQuestionOptionForm, SequenceQuestionElementForm, ComparisonQuestionElementForm
from .models import Test, Comment, TestRate, Tag, Category, QuestionOfTest
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import QueryDict
import re

# Модель пользователя
User = get_user_model()

def get_tests_lists_context():
    showing_tests_per_one_column = 14
    showing_tags_and_categories_amount = 58

    # Левый ряд тестов для списка новых тестов, диапазон от 0го до showing_tests_per_one_column - 1
    left_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date', 'name')[:showing_tests_per_one_column]
    # Левый ряд тестов для списка новых тестов
    right_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date', 'name')[showing_tests_per_one_column:showing_tests_per_one_column*2]
    # Левый ряд тестов для списка рейтинговых тестов, диапазон от 0го до showing_tests_per_one_column - 1
    left_number_of_rating_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[:showing_tests_per_one_column]
    # Левый ряд тестов для списка рейтинговых тестов
    right_number_of_rating_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[showing_tests_per_one_column:showing_tests_per_one_column*2]

    # Создаем и сортируем массив массивов [тег, количество опубликованных тестов с этим тегом]
    showing_tags_and_count_of_published_tests = []
    for tag in Tag.objects.order_by('name')[:showing_tags_and_categories_amount]:
        showing_tags_and_count_of_published_tests.append([tag, tag.tests.filter(published_date__lte=timezone.now()).count()])
    showing_tags_and_count_of_published_tests.sort(key=lambda i: i[1], reverse=True)

    # Создаем и сортируем массив массивов [категория, количество опубликованных тестов с этой категорией]
    showing_categories_and_count_of_published_tests = []
    for category in Category.objects.filter(confirmed=True).order_by('name')[:showing_tags_and_categories_amount]:
        showing_categories_and_count_of_published_tests.append([category, category.tests.filter(published_date__lte=timezone.now()).count()])
    showing_categories_and_count_of_published_tests.sort(key=lambda i: i[1], reverse=True)

    all_tags_count = Tag.objects.count()

    all_published_test_count = Test.objects.filter(published_date__lte=timezone.now()).count()
    all_confirmed_categories_count = Category.objects.filter(confirmed=True).count()

    # Определяем, показывать ли значки-многоточия под списками.
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

def get_filtered_and_sorted_tests_with_pagination(request, tests, on_one_page, max_pages_before_or_after_current):
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
    pag_context = get_pagination(page, tests, on_one_page, max_pages_before_or_after_current)
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

def get_categories_with_count_of_published_tests(categories):
    # Нужно изменить количество тестов, выводимых при фильтрации по категории
    categories_and_count_of_published_tests_in_them = []
    for category in categories:
        categories_and_count_of_published_tests_in_them.append([category, category.tests.filter(published_date__lte=timezone.now()).count()])
    categories_and_count_of_published_tests_in_them.sort(key=lambda i: i[1], reverse=True)
    return categories_and_count_of_published_tests_in_them

def get_tags_with_count_of_published_tests(tags):
    # Нужно изменить количество тестов, выводимых при фильтрации по тегу
    tags_and_count_of_published_tests_in_them = []
    for tag in tags:
        tags_and_count_of_published_tests_in_them.append([tag, tag.tests.filter(published_date__lte=timezone.now()).count()])
    tags_and_count_of_published_tests_in_them.sort(key=lambda i: i[1], reverse=True)        
    return tags_and_count_of_published_tests_in_them

# 3 списка тестов (№ 2, № 3, № 4), на которые можно перейти из главной страницы
def tests(request):
    # Если сортировка не задана, то тесты будут по алфавиту
    tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('name')
    categories = Category.objects.filter(confirmed=True).order_by('name')    
    categories_with_count_of_published_tests = get_categories_with_count_of_published_tests(categories)
    tags = Tag.objects.order_by('name')    
    tags_with_count_of_published_tests = get_tags_with_count_of_published_tests(tags)
    context = get_filtered_and_sorted_tests_with_pagination(request, tests, 35, 5)
    context['categories_for_filtering_of_tests'] = categories_with_count_of_published_tests
    context['tags_for_filtering_of_tests'] = tags_with_count_of_published_tests
    return render(request, 'octapp/tests.html', context)

def categories(request):
    categories = Category.objects.filter(confirmed=True).order_by('name')
    categories_with_count_of_published_tests = get_categories_with_count_of_published_tests(categories)
    context = get_pagination(int(request.GET.get('page', '1')), categories_with_count_of_published_tests, 35, 5)
    return render(request, 'octapp/categories.html', context)

def tags(request):
    tags = Tag.objects.order_by('name')
    tags_with_count_of_published_tests = get_tags_with_count_of_published_tests(tags)
    context = get_pagination(int(request.GET.get('page', '1')), tags_with_count_of_published_tests, 35, 5)
    return render(request, 'octapp/tags.html', context)

@login_required
def user_tests(request, pk):
    user_tests = Test.objects.filter(author=request.user).order_by('name')
    context = get_filtered_and_sorted_tests_with_pagination(request, user_tests, 14, 5)
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
    if request.method == 'POST':
        # Form форма с пользовательскими данными
        form = TestForm(request.POST)
        if form.is_valid():
            # Если использовать form.save(commit=False), то выбранные пользователем теги к тесту не добавляются!
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
    test = get_object_or_404(Test, pk=pk)
    if request.user == test.author:
        is_author = True
    else:
        is_author = False
    # Если тест еще не опубликован и текущий пользователь — не автор
    # Чтобы предотвратить возможность просмотра неопубликованного теста через URL
    if test.published_date:
        if not is_author and test.published_date > timezone.now():
            return redirect('tests_lists')
    else:
        if not is_author:
            return redirect('tests_lists')
    if not request.user.is_authenticated:
        return render(request, 'octapp/test_detail.html', {'test': test })
    else:
        try:
            rate_of_current_user = TestRate.objects.get(test=test, reviewer=request.user)
            return render(request, 'octapp/test_detail.html', {'test': test, 'is_author': is_author, 'rate_of_current_user': rate_of_current_user })
        # Пользователь еще не ставил оценку данному тесту
        except TestRate.DoesNotExist:
            return render(request, 'octapp/test_detail.html', {'test': test, 'is_author': is_author })

@login_required
def test_edit(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == 'POST':
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

def get_questions_of_test_context(test_id, page):
    test = get_object_or_404(Test, pk=test_id)
    questions_of_test = test.questions_of_test.order_by('question_index_number')
    questions_of_test_with_filled_forms = []

    # Генерация двумерного списка с вопросами теста и соответствующими заполненными формами,
    # чтобы иметь возможность выводить эти формы для редактирования вопросов
    # Через атрибут auto_id переопределяются id элементов форм. Без переопределения id у форм будут
    # одинаковы — id_question_content (в случае вопросов закрытого типа, поле с контентом которых называется question_content),
    # что приведет к тому, что js скрипты для ckeditor’а не будут работать для этих полей должным образом —
    # будет отображаться лишь стандартный HTML-тег textarea.
    for question_of_test in questions_of_test:
        plug = None
        if question_of_test.type_of_question == 'ClsdQ':
            closed_question_form = ClosedQuestionForm(instance=question_of_test.closed_question,
                                                      initial={'question_index_number': question_of_test.question_index_number},
                                                      auto_id='id_for_' + str(question_of_test.question_index_number) + '_%s')
            closed_question_option_form = ClosedQuestionOptionForm(auto_id='id_for_new_option_form_qu_' + str(question_of_test.question_index_number) + '_%s')
            # 4’ый элемент списка — форма для добавления элементов правого ряда сопоставления, а в случае вопросов других типов ее нет, поэтому используется з
            questions_of_test_with_filled_forms.append([question_of_test, closed_question_form, closed_question_option_form, plug])
        elif question_of_test.type_of_question == 'OpndQ':
            open_question_form = OpenQuestionForm(instance=question_of_test.open_question,
                                                  initial={'question_index_number': question_of_test.question_index_number},
                                                  auto_id='id_for_' + str(question_of_test.question_index_number) + '_%s')
            questions_of_test_with_filled_forms.append([question_of_test, open_question_form, plug, plug])
        elif question_of_test.type_of_question == 'SqncQ':
            sequence_question_form = SequenceQuestionForm(instance=question_of_test.sequence_question,
                                                          initial={'question_index_number': question_of_test.question_index_number},
                                                          auto_id='id_for_' + str(question_of_test.question_index_number) + '_%s')
            sequence_question_element_form = SequenceQuestionElementForm(auto_id='id_for_new_sequ_el_form_qu_' + str(question_of_test.question_index_number) + '_%s')
            questions_of_test_with_filled_forms.append([question_of_test, sequence_question_form, sequence_question_element_form, plug])
        elif question_of_test.type_of_question == 'CmprsnQ':
            comparison_question_form = ComparisonQuestionForm(instance=question_of_test.comparison_question,
                                                              initial={'question_index_number': question_of_test.question_index_number},
                                                              auto_id='id_for_' + str(question_of_test.question_index_number) + '_%s')
            comparison_question_left_row_element_form = ComparisonQuestionElementForm(auto_id='id_for_new_comp_left_el_form_qu_' + str(question_of_test.question_index_number) + '_%s')
            comparison_question_right_row_element_form = ComparisonQuestionElementForm(auto_id='id_for_new_comp_right_el_form_qu_' + str(question_of_test.question_index_number) + '_%s')

            questions_of_test_with_filled_forms.append([question_of_test, comparison_question_form, comparison_question_left_row_element_form, comparison_question_right_row_element_form])

    # 4 формы для добавления вопросов соответствующих типов
    closed_question_form = ClosedQuestionForm()
    open_question_form = OpenQuestionForm()
    sequence_question_form = SequenceQuestionForm()
    comparison_question_form = ComparisonQuestionForm()

    context = {'test': test,
               'closed_question_form': closed_question_form,
               'open_question_form': open_question_form,
               'sequence_question_form': sequence_question_form,
               'comparison_question_form': comparison_question_form}
    pag_context = get_pagination(page, questions_of_test_with_filled_forms, 12, 4)
    context.update(pag_context)
    return context

@login_required
def questions_of_test(request, test_id):
    page = request.GET.get('page', '1')
    page = int(page)
    return render(request, 'octapp/questions_of_test.html', get_questions_of_test_context(test_id, page))

@login_required
def new_question(request, test_id, type):
    # Пустые формы для контекста
    closed_question_form = ClosedQuestionForm()
    open_question_form = OpenQuestionForm()
    sequence_question_form = SequenceQuestionForm()
    comparison_question_form = ComparisonQuestionForm()

    test = get_object_or_404(Test, pk=test_id)
    questions_of_test = test.questions_of_test.order_by('question_index_number')
    index_number_of_new_test_question = test.questions_of_test.count() + 1
    if type == 'closed':
        if request.method == 'POST':
            # Form форма с пользовательскими данными
            closed_question_form = ClosedQuestionForm(request.POST)
            if closed_question_form.is_valid():
                new_question_of_test = QuestionOfTest.objects.create(test=test,
                        type_of_question='ClsdQ', question_index_number=index_number_of_new_test_question)
                # Пока не сохраняем объект
                new_closed_question_object = closed_question_form.save(commit=False)
                new_closed_question_object.question_of_test = new_question_of_test
                new_closed_question_object.save()
                return redirect('questions_of_test', test_id=test_id)
        else:
            # Пустая форма
            closed_question_form = ClosedQuestionForm()

    if type == 'open':
        if request.method == 'POST':
            # Form форма с пользовательскими данными
            open_question_form = OpenQuestionForm(request.POST)
            if open_question_form.is_valid():
                new_question_of_test = QuestionOfTest.objects.create(test=test,
                        type_of_question='OpndQ', question_index_number=index_number_of_new_test_question)
                # Пока не сохраняем объект
                new_open_question_object = open_question_form.save(commit=False)
                new_open_question_object.question_of_test = new_question_of_test
                new_open_question_object.save()
                return redirect('questions_of_test', test_id=test_id)
        else:
            # Пустая форма
            open_question_form = OpenQuestionForm()

    if type == 'sequence':
        if request.method == 'POST':
            # Form форма с пользовательскими данными
            sequence_question_form = SequenceQuestionForm(request.POST)
            if sequence_question_form.is_valid():
                new_question_of_test = QuestionOfTest.objects.create(test=test,
                        type_of_question='SqncQ', question_index_number=index_number_of_new_test_question)
                # Пока не сохраняем объект
                new_sequence_question_object = sequence_question_form.save(commit=False)
                new_sequence_question_object.question_of_test = new_question_of_test
                new_sequence_question_object.save()
                return redirect('questions_of_test', test_id=test_id)
        else:
            # Пустая форма
            sequence_question_form = SequenceQuestionForm()

    if type == 'comparison':
        if request.method == 'POST':
            # Form форма с пользовательскими данными
            comparison_question_form = ComparisonQuestionForm(request.POST)
            if comparison_question_form.is_valid():
                new_question_of_test = QuestionOfTest.objects.create(test=test,
                        type_of_question='CmprsnQ', question_index_number=index_number_of_new_test_question)
                # Пока не сохраняем объект
                new_comparison_question_object = comparison_question_form.save(commit=False)
                new_comparison_question_object.question_of_test = new_question_of_test
                new_comparison_question_object.save()
                return redirect('questions_of_test', test_id=test_id)
        else:
            # Пустая форма
            comparison_question_form = ComparisonQuestionForm()
    return render(request, 'octapp/questions_of_test.html', {'test': test,
                        'questions_of_test': questions_of_test,
                        'closed_question_form': closed_question_form,
                        'open_question_form': open_question_form,
                        'sequence_question_form': sequence_question_form,
                        'comparison_question_form': comparison_question_form})

@login_required
def question_edit(request, test_id, question_of_test_id):
    test = get_object_or_404(Test, pk=test_id)
    question_of_test = get_object_or_404(QuestionOfTest, pk=question_of_test_id)
    page = request.GET.get('page', '1')
    page = int(page)
    if request.method == 'POST':
        if question_of_test.type_of_question == 'ClsdQ':
            form = ClosedQuestionForm(request.POST, instance=question_of_test.closed_question)
        elif question_of_test.type_of_question == 'OpndQ':
            form = OpenQuestionForm(request.POST, instance=question_of_test.open_question)
        elif question_of_test.type_of_question == 'SqncQ':
            form = SequenceQuestionForm(request.POST, instance=question_of_test.sequence_question)
        elif question_of_test.type_of_question == 'CmprsnQ':
            form = ComparisonQuestionForm(request.POST, instance=question_of_test.comparison_question)
        if form.is_valid():
            new_index = form.cleaned_data['question_index_number']
            old_index = question_of_test.question_index_number
            if new_index != old_index:
                if new_index > test.questions_of_test.count():
                    new_index = test.questions_of_test.count()
                qus_of_test = get_object_or_404(QuestionOfTest, test=test, question_index_number=new_index)
                qus_of_test.question_index_number = old_index
                qus_of_test.save()
            certain_type_question_from_form = form.save(commit=False)
            certain_type_question_from_form.question_of_test.question_index_number = new_index
            certain_type_question_from_form.question_of_test.save()
            certain_type_question_from_form.save()
            return redirect('questions_of_test', test_id)
    else:
        return render(request, 'octapp/questions_of_test.html', get_questions_of_test_context(test_id, page))

@login_required
def question_remove(request, test_id, question_of_test_id):
    test = get_object_or_404(Test, pk=test_id)
    question_of_test = get_object_or_404(QuestionOfTest, pk=question_of_test_id)

    # Коррекция порядковых номеров последующих вопросов
    farther_questions = test.questions_of_test.all().order_by('question_index_number')[question_of_test.question_index_number:]
    for father_question in farther_questions:
        father_question.question_index_number -= 1
        father_question.save()

    question_of_test.delete()
    return redirect('questions_of_test', test_id=test_id)


@login_required
def review(request, test_id, user_rate):
    test = get_object_or_404(Test, pk=test_id)
    user = request.user
    # Устранение возможности голосовать за других пользователей с помощью ввода URL
    if user == request.user:
        if user_rate == 'like':
            bool_rate = True
        elif user_rate == 'dislike':
            bool_rate = False
        # Пользователь еще не ставил оценку данному тесту
        if not test.rates.filter(reviewer=user):
            # Создаем новый объект модели TestRate для данного пользователя, теста и оценки, а также
            # добавляем его в связанные объекты объекта Test
            test_rate = TestRate(test=test, reviewer=user, like=bool_rate)
            test_rate.save(force_insert=True)
            if user_rate == 'like':
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

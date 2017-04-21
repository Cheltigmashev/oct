from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TestForm
from .models import Test, Comment, Test_rate, Tag, Category
from django.contrib.auth import get_user_model
from django.contrib.auth import views as auth_views

# Модель пользователя
User = get_user_model()

def get_tests_lists_context():
    # левый ряд тестов для списка новых тестов, диапазон от 0го до 19го
    left_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[:20]
    # левый ряд тестов для списка новых тестов, диапазон от 20го до 40го
    right_number_of_new_tests_list = Test.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')[20:41]
    # левый ряд тестов для списка рейтинговых тестов, диапазон от 0го до 19го
    left_number_of_popular_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[:20]
    # левый ряд тестов для списка рейтинговых тестов, диапазон от 20го до 40го
    right_number_of_popular_tests = Test.objects.filter(published_date__lte=timezone.now()).order_by('-rating', 'name')[20:41]
    tests_lists_context = {'left_number_of_new_tests_list': left_number_of_new_tests_list,
        'right_number_of_new_tests_list': right_number_of_new_tests_list,
        'left_number_of_popular_tests': left_number_of_popular_tests,
        'right_number_of_popular_tests': right_number_of_popular_tests}
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
            if form.cleaned_data['new_category'] and not form.cleaned_data['category']:
                some_new_category = Category.objects.create(name=form.cleaned_data['new_category'].capitalize())
                test.category = some_new_category
            if form.cleaned_data['new_tags']:
                new_tags = form.cleaned_data['new_tags'].split(',')
                for item in new_tags:
                    # Если такого тега еще нет в базе
                    if not Tag.objects.filter(name__iexact=item.strip(' \t\n\r')):
                        new_tag_object = Tag.objects.create(name=item.strip(' \t\n\r'))
                        test.tags.add(new_tag_object)
                    # Если такой тег уже есть в базе
                    else:
                        test.tags.add(Tag.objects.filter(name__iexact=item.strip(' \t\n\r')))
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
    try:
        user_review = Test_rate.objects.get(test=test, reviewer=request.user)
        return render(request, 'octapp/test_detail.html', {'test': test, 'is_author': is_author, 'user_review': user_review })
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
def test_publish(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.publish()
    return redirect('test_detail', pk=pk)

@login_required
def test_make_ready_for_passing(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.make_ready_for_passing()
    return redirect('test_detail', pk=pk)

@login_required
def test_remove(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.delete()
    return redirect('tests_lists')

@login_required
def test_remove_through_user_tests(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.delete()
    return redirect('user_tests', pk=pk)

@login_required
def review(request, test_id, user_rate, user_id):
    test = get_object_or_404(Test, pk=test_id)
    user = get_object_or_404(User, pk=user_id)
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

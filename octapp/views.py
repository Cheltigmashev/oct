from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import TestForm
from .models import Test, Comment

# Представление главной страницы
def tests_lists(request):
    return render(request, 'octapp/tests_lists.html', {})

@login_required
def test_adding(request):
    if request.method == "POST":
        # Form форма с пользовательскими данными
        form = TestForm(request.POST)
        if form.is_valid():
            # Пока не сохранять модель Test
            test = form.save(commit=False)
            test.author = request.user
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
    return render(request, 'octapp/test_detail.html', {'test': test})

@login_required
def test_edit(request, pk):
    test = get_object_or_404(Test, pk=pk)
    if request.method == "POST":
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            test = form.save(commit=False)
            test.author = request.user
            test.save()
            return redirect('test_detail', pk=test.pk)
    else:
        form = TestForm(instance=test)
    return render(request, 'blog/test_edit.html', {'form': form})

@login_required
def test_publish(request, pk):
    test = get_object_or_404(Test, pk=pk)
    test.publish()
    return redirect('test_detail', pk=pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    test_pk = comment.test.pk
    comment.delete()
    return redirect('test_detail', pk=test_pk)

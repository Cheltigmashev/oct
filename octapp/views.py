from django.shortcuts import render

# View of main page.
def tests_lists(request):
    return render(request, 'octapp/tests_lists.html', {})

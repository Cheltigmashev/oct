from django.shortcuts import render

# Create your views here.
def tests_list(request):
    return render(request, 'octapp/tests_list.html', {})

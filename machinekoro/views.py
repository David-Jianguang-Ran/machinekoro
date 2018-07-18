from django.shortcuts import render

# Create your views here.


# place holder views

def cover_view(request):
    return render(request, 'static.html')


def main_view(request):
    return render(request, 'reactEnabled.html')

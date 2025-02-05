from django.shortcuts import render

def apresentation_view(request):
    return render(request, 'comum/apresentation.html')
    

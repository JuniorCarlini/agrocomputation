from functools import wraps
from django.http import JsonResponse
from irrigation.models import Configuration

def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return JsonResponse(
                {'error': 'Missing authorization token'}, 
                status=401
            )
            
        try:
            config = Configuration.objects.latest('created_at')
            if token != config.token:
                return JsonResponse(
                    {'error': 'Invalid token'}, 
                    status=403
                )
        except Configuration.DoesNotExist:
            return JsonResponse(
                {'error': 'Configuration not found'}, 
                status=404
            )
            
        return view_func(request, *args, **kwargs)
        
    return wrapper
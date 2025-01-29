from django.contrib.auth import get_user_model

def dashboard_callback(request, context):
    User = get_user_model()
    context.update({
        "total_users": User.objects.count(),
    })
    return context
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import tempfile
from users.models import CustomUser, UserMatch, UserBook
from users.matching import batch_match_users, shuffle_connection
from users.import_books import import_books

@csrf_exempt
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file') and request.POST.get('user_id'):
        user = get_object_or_404(CustomUser, id=request.POST['user_id'])
        csv_file = request.FILES['csv_file']

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            for chunk in csv_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        import_books(tmp_path, user)
        return JsonResponse({'success': 'yayy ur books have been imported !!'})
    return JsonResponse({'error': 'no file or user has been given ;('})

def trigger_match(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        batch_match_users()

        matches = UserMatch.objects.filter(user=user)
        data = {'matches': [m.matched_user.username for m in matches]}
        return JsonResponse(data)

    return JsonResponse({'error': 'this is invalid :((('})

def shuffle_match(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, id=user_id)

        existing_matches = UserMatch.objects.filter(user=user)
        removed = [m.matched_user.username for m in existing_matches]

        shuffle_connection(user)

        new_matches = UserMatch.objects.filter(user=user)
        data = {
            'removed': removed,
            'new matches': [m.matched_user.username for m in new_matches],
            'previous matches': [u.username for u in user.previous_matches.all()],
        }
        return JsonResponse(data)

    return JsonResponse({'error': 'this is invalid :((('})

def view_matches(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    matches = UserMatch.objects.filter(user=user)
    prev = [u.username for u in user.previous_matches.all()]
    return JsonResponse({
        'matches': [m.matched_user.username for m in matches],
        'previous matches': prev,
    })

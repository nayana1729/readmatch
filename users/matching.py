from users.models import CustomUser, Genre, Book
from matches.models import Match
import numpy as np
from numpy.linalg import norm

all_genres = list(Genre.objects.all())
genre_name_to_index = {genre.name: idx for idx, genre in enumerate(all_genres)}

def build_user_vector(user: CustomUser):
    vector = []

    for q, answer in sorted(user.quiz_answers.items()):
        vector.append(answer)

    genre_vector = [0] * len(all_genres)
    for genre in user.favorite_genres.all():
        idx = genre_name_to_index[genre.name]
        genre_vector[idx] = 1
    vector.extend(genre_vector)

    books = user.books_read.all()
    num_books = len(books)
    avg_pages = np.mean([book.page_count for book in books]) if books else 0
    vector.extend([num_books, avg_pages])

    return np.array(vector, dtype=float)

def cosine_similarity(vec1, vec2):
    if norm(vec1) == 0 or norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

def compute_matches_partial(user: CustomUser, max_matches_per_user=2):
    users = list(CustomUser.objects.all())
    vectors = {u.id: build_user_vector(u) for u in users}

    connections = {u.id: [] for u in users}
    past_matches = set()
    for m in Match.objects.all():
        if m.user == user:
            if m.primary_match:
                past_matches.add(m.primary_match.id)
            if m.secondary_match:
                past_matches.add(m.secondary_match.id)
            for pm in m.previous_matches.all():
                past_matches.add(pm.id)
        if m.primary_match:
            connections[m.user.id].append(m.primary_match.id)
        if m.secondary_match:
            connections[m.user.id].append(m.secondary_match.id)

    if len(connections[user.id]) >= max_matches_per_user:
        return

    best_user = None
    best_score = -1
    vec_a = vectors[user.id]

    for user_b in users:
        if user.id == user_b.id:
            continue
        if len(connections[user_b.id]) >= max_matches_per_user:
            continue
        if user_b.id in connections[user.id]:
            continue
        if user_b.id in past_matches:
            continue

        score = cosine_similarity(vec_a, vectors[user_b.id])
        if score > best_score:
            best_score = score
            best_user = user_b

    if best_user:
        m, created = Match.objects.get_or_create(user=user)
        if not m.primary_match:
            m.primary_match = best_user
        elif not m.secondary_match:
            m.secondary_match = best_user

        m.previous_matches.add(best_user)
        m.save()

def shuffle_user(user: CustomUser):
    try:
        m = Match.objects.get(user=user)

        if m.primary_match:
            pm = Match.objects.filter(user=m.primary_match).first()
            if pm:
                if pm.primary_match == user:
                    pm.primary_match = None
                if pm.secondary_match == user:
                    pm.secondary_match = None
                pm.save()

        if m.secondary_match:
            sm = Match.objects.filter(user=m.secondary_match).first()
            if sm:
                if sm.primary_match == user:
                    sm.primary_match = None
                if sm.secondary_match == user:
                    sm.secondary_match = None
                sm.save()

        m.primary_match = None
        m.secondary_match = None
        m.save()
    except Match.DoesNotExist:
        pass

    compute_matches_partial(user)

import hashlib
import numpy as np
from numpy.linalg import norm
from django.db import transaction
from django.utils import timezone
from users.models import CustomUser, UserBook, UserMatch
from users.import_books import recent_years, min_books, max_books
from django.conf import settings

max_matches = 2

def eligible(u: CustomUser) -> bool:
    return bool(u.quiz_genres) and UserBook.objects.filter(user=u).count() >= min_books

def count(u: CustomUser) -> int:
    return UserMatch.objects.filter(user=u).count()

def already_matched(u: CustomUser, v: CustomUser) -> bool:
    return UserMatch.objects.filter(user=u, matched_user=v).exists() or \
           UserMatch.objects.filter(user=v, matched_user=u).exists()

def create_mutual(u: CustomUser, v: CustomUser) -> None:
    UserMatch.objects.get_or_create(user=u, matched_user=v)
    UserMatch.objects.get_or_create(user=v, matched_user=u)

def delete_mutual(u: CustomUser, v: CustomUser) -> None:
    UserMatch.objects.filter(user=u, matched_user=v).delete()
    UserMatch.objects.filter(user=v, matched_user=u).delete()

def exclusions(u: CustomUser) -> set[int]:
    cur = set(UserMatch.objects.filter(user=u).values_list('matched_user_id', flat=True))
    prev = set(u.previous_matches.values_list('id', flat=True))
    return cur.union(prev, {u.id})

def noise(seed: str, lo: float = -0.25, hi: float = 0.25) -> float:
    h = hashlib.md5(seed.encode()).hexdigest()
    x = int(h[:8], 16) / 0xFFFFFFFF
    return lo + (hi - lo) * x

def build_user_vector(user: CustomUser) -> np.ndarray:
    if not eligible(user):
        n_genres = len(user.quiz_genres) if user.quiz_genres else 0
        return np.zeros(n_genres + 3, dtype=float)

    vec = []

    for genre, rating in sorted(user.quiz_genres.items()):
        base = float(rating)
        n = noise(f"{user.username}:{genre}", -0.3, 0.3)
        vec.append(base + n)

    qs = UserBook.objects.filter(user=user).order_by("-date_read")
    books = list(qs[:max_books])
    today = timezone.now().date()

    ratings, pages, weights = [], [], []
    for ub in books:
        if ub.date_read:
            years_ago = (today - ub.date_read).days / 365.0
            rec_w = 1.0 + max(0.0, (recent_years - years_ago)) / recent_years
        else:
            rec_w = 1.0
        ratings.append(float(ub.my_rating or 0.0))
        pages.append(float(ub.book.num_pages or 0.0))
        weights.append(rec_w)

    avg_pages = float(np.average(pages, weights=weights)) if pages else 0.0
    avg_rating = float(np.average(ratings, weights=weights)) if ratings else 0.0
    num_books = float(len(books))

    vec.extend([
        num_books / max_books,
        (avg_pages / 600.0) + noise(f"{user.username}:pages", -0.03, 0.03),
        (avg_rating / 5.0) + noise(f"{user.username}:rating", -0.03, 0.03),
    ])

    return np.array(vec, dtype=float)

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    if v1.size == 0 or v2.size == 0:
        return 0.0
    n1, n2 = norm(v1), norm(v2)
    if n1 == 0.0 or n2 == 0.0:
        return 0.0
    return float(np.dot(v1, v2) / (n1 * n2))

@transaction.atomic
def batch_match_users() -> None:
    all_users = list(CustomUser.objects.order_by("date_joined"))
    users = [u for u in all_users if eligible(u)]
    if len(users) < 2:
        return

    vectors = {u.id: build_user_vector(u) for u in users}
    exclusion_map = {u.id: exclusions(u) for u in users}
    counts = {u.id: count(u) for u in users}
    id2u = {u.id: u for u in users}

    pairs = []
    for i, ui in enumerate(users):
        for j in range(i + 1, len(users)):
            uj = users[j]
            if uj.id in exclusion_map[ui.id] or ui.id in exclusion_map[uj.id]:
                continue
            score = cosine_similarity(vectors[ui.id], vectors[uj.id])
            if score > 0.0:
                pairs.append((score, ui.date_joined, uj.date_joined, ui.id, uj.id))

    pairs.sort(key=lambda t: (-t[0], t[1], t[2]))

    for score, joined1, joined2, uid, vid in pairs:
        if counts[uid]>= max_matches or counts[vid] >= max_matches:
            continue
        u, v = id2u[uid], id2u[vid]
        create_mutual(u, v)
        counts[uid] += 1
        counts[vid] += 1

    for score, joined1, joined2, uid, vid in pairs:
        u_c, v_c = counts[uid], counts[vid]
        if not ((u_c == 0 and v_c < max_matches) or (v_c == 0 and u_c < max_matches)):
            continue
        u, v = id2u[uid], id2u[vid]
        if already_matched(u, v):
            continue
        create_mutual(u, v)
        counts[uid] += 1
        counts[vid] += 1

@transaction.atomic
def shuffle_connection(shuffler: CustomUser) -> None:
    partner_ids = list(
        UserMatch.objects.filter(user=shuffler).values_list("matched_user_id", flat=True)
    )
    partners = list(CustomUser.objects.filter(id__in=partner_ids))

    if settings.DEBUG:
        print(f"\n[shuffle] before for {shuffler.username}: {[p.username for p in partners]}")

    for p in partners:
        delete_mutual(shuffler, p)
        shuffler.previous_matches.add(p)
        p.previous_matches.add(shuffler)

    if settings.DEBUG:
        print(f"[shuffle] after deletion for {shuffler.username}: []")

    assign_new(shuffler, 1, exclude_ids=exclusions(shuffler))

    if settings.DEBUG:
        print(f"[shuffle] after shuffle for {shuffler.username}: "
          f"{[m.matched_user.username for m in shuffler.user_matches.all()]}")

def assign_new(user: CustomUser, n: int, exclude_ids: set[int]) -> None:
    if not eligible(user):
        return
    if count(user) >= max_matches:
        return

    u_vec = build_user_vector(user)
    others = [o for o in CustomUser.objects.exclude(id__in=exclude_ids) if eligible(o)]

    scored = []
    for o in others:
        oc = count(o)
        if oc >= max_matches:
            continue
        score = cosine_similarity(u_vec, build_user_vector(o))
        if score > 0.0:
            scored.append((score, oc, o.date_joined, o))

    scored.sort(key=lambda t: (-t[0], t[1], t[2]))

    for score, partner_matches, joined_at, match in scored:
        if count(user) >= max_matches:
            break
        if count(match) >= max_matches:
            continue
        create_mutual(user, match)

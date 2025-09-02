# match_users.py
# -----------------------------
# Make Django environment available
import os
import sys

# 🔹 Ensure project root is in Python path
# __file__ = .../users/management/commands/match_users.py
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(PROJECT_ROOT)

# 🔹 Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "readmatch.settings")

# 🔹 Initialize Django
import django
django.setup()

# 3️⃣ Now you can import Django models and any app code
from users.models import CustomUser, Genre, Book
from matches.models import Match
from matching import build_user_vector, cosine_similarity, compute_matches_partial, shuffle_user
import numpy as np

# -----------------------------
# 4️⃣ Create test data
# -----------------------------
def create_test_data():
    # Clear existing users, books, genres
    Match.objects.all().delete()
    CustomUser.objects.all().delete()
    Book.objects.all().delete()
    Genre.objects.all().delete()

    # Genres
    fantasy = Genre.objects.create(name="Fantasy")
    scifi = Genre.objects.create(name="Sci-Fi")
    romance = Genre.objects.create(name="Romance")

    # Books
    hp = Book.objects.create(title="Harry Potter", author="J.K. Rowling", page_count=500, year_published=1997)
    lotr = Book.objects.create(title="Lord of the Rings", author="J.R.R. Tolkien", page_count=1000, year_published=1954)

    # Users
    alice = CustomUser.objects.create_user(username="alice", password="pass123")
    bob = CustomUser.objects.create_user(username="bob", password="pass123")
    carol = CustomUser.objects.create_user(username="carol", password="pass123")

    # Assign favorite genres
    alice.favorite_genres.add(fantasy, romance)
    bob.favorite_genres.add(fantasy)
    carol.favorite_genres.add(scifi, romance)

    # Assign books read
    alice.books_read.add(hp)
    bob.books_read.add(hp, lotr)
    carol.books_read.add(lotr)

    # Assign quiz answers (numeric for simplicity)
    alice.quiz_answers = {"book_length": 0, "style": 0, "tropes": 2}  # short, descriptive, 2 tropes
    bob.quiz_answers = {"book_length": 0, "style": 0, "tropes": 2}
    carol.quiz_answers = {"book_length": 2, "style": 2, "tropes": 1}
    alice.save()
    bob.save()
    carol.save()

    return [alice, bob, carol]

# -----------------------------
# 5️⃣ Display matches
# -----------------------------
def display_matches():
    print("--- Current Matches ---")
    for m in Match.objects.all():
        print(f"{m.user.username} -> primary: {getattr(m.primary_match, 'username', None)}, "
              f"secondary: {getattr(m.secondary_match, 'username', None)}")
    print("-----------------------")

# -----------------------------
# 6️⃣ Main flow
# -----------------------------
if __name__ == "__main__":
    users = create_test_data()

    # Compute initial matches
    for user in users:
        compute_matches_partial(user)

    display_matches()

    # Example shuffle
    print("\n--- Shuffling Alice ---")
    shuffle_user(users[0])
    display_matches()

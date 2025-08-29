from users.models import CustomUser, Genre, Book
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
    return np.dot(vec1, vec2) / (norm(vec1) * norm(vec2))

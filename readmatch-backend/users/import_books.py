import csv
from django.utils import timezone
from datetime import datetime, date
from users.models import Book, UserBook, CustomUser

recent_years = 5
min_books = 50
max_books = 150

def import_books(file_path: str, user: CustomUser) -> bool:
    today = timezone.now().date()
    imported_books = []

    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            only_read = row.get("Exclusive Shelf", "").strip().lower()
            if only_read != "read":
                continue
            book_id = row.get("Book Id") or None
            title = (row.get("Title") or "").strip()
            author = (row.get("Author") or "").strip()
            additional_authors = row.get("Additional Authors", "")
            average_rating = safe_float(row.get("Average Rating"))
            num_pages = safe_int(row.get("Number of Pages"))
            year_published = safe_int(row.get("Year Published"))
            user_rating = safe_int(row.get("My Rating"))
            date_read = parse_date(row.get("Date Read"))

            if not title:
                continue

            imported_books.append({
                "book_id": book_id,
                "title": title,
                "author": author,
                "additional_authors": additional_authors,
                "average_rating": average_rating,
                "num_pages": num_pages,
                "year_published": year_published,
                "user_rating": user_rating,
                "date_read": date_read or today,
            })

    imported_books.sort(key=lambda x: x["date_read"], reverse=True)

    total_books = len(imported_books)
    if total_books < min_books:
        return False
    if total_books > max_books:
        imported_books = imported_books[:max_books]

    for b in imported_books:
        book, _ = Book.objects.update_or_create(
            book_id=b["book_id"],
            defaults={
                "title": b["title"],
                "author": b["author"],
                "additional_authors": b["additional_authors"],
                "average_rating": b["average_rating"],
                "num_pages": b["num_pages"],
                "year_published": b["year_published"],
            },
        )

        UserBook.objects.update_or_create(
            user=user,
            book=book,
            defaults={
                "my_rating": b["user_rating"],
                "date_read": b["date_read"],
            },
        )
    return True


def safe_float(val: str | None) -> float:
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def safe_int(val: str | None) -> int:
    try:
        return int(val) if val else 0
    except (ValueError, TypeError):
        return 0

def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None
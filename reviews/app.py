import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "reviews.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS places (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
            comment TEXT NOT NULL,
            place_id INTEGER NOT NULL,
            FOREIGN KEY (place_id) REFERENCES places (id)
        )
    """)

    places_count = conn.execute("SELECT COUNT(*) FROM places").fetchone()[0]
    if places_count == 0:
        conn.executemany(
            "INSERT INTO places (name) VALUES (?)",
            [
                ("Кофейня",),
                ("Бургерная",),
                ("Пиццерия",),
            ]
        )

    reviews_count = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    if reviews_count == 0:
        conn.executemany(
            "INSERT INTO reviews (username, rating, comment, place_id) VALUES (?, ?, ?, ?)",
            [
                ("Иван", 5, "Всё отлично", 1),
                ("Анна", 4, "Хорошее место", 2),
                ("Алексей", 2, "Обслуживание медленное", 3),
            ]
        )

    conn.commit()
    conn.close()


@app.route("/")
def index():
    rating_filter = request.args.get("rating", "").strip()
    conn = get_db_connection()

    try:
        if rating_filter.isdigit():
            rating_filter = int(rating_filter)
            reviews = conn.execute("""
                SELECT reviews.*, places.name AS place_name
                FROM reviews
                JOIN places ON reviews.place_id = places.id
                WHERE reviews.rating = ?
            """, (rating_filter,)).fetchall()
        else:
            reviews = conn.execute("""
                SELECT reviews.*, places.name AS place_name
                FROM reviews
                JOIN places ON reviews.place_id = places.id
            """).fetchall()
    except sqlite3.Error:
        return "Ошибка при чтении данных из базы", 500
    finally:
        conn.close()

    return render_template("index.html", reviews=reviews, current_filter=rating_filter)


@app.route("/reviews/<int:review_id>")
def detail(review_id):
    conn = get_db_connection()

    try:
        review = conn.execute("""
            SELECT reviews.*, places.name AS place_name
            FROM reviews
            JOIN places ON reviews.place_id = places.id
            WHERE reviews.id = ?
        """, (review_id,)).fetchone()
    except sqlite3.Error:
        return "Ошибка при обращении к базе данных", 500
    finally:
        conn.close()

    if review is None:
        return "Отзыв не найден", 404

    return render_template("detail.html", review=review)


@app.route("/reviews/add", methods=["GET", "POST"])
def add_review():
    conn = get_db_connection()

    try:
        places = conn.execute("SELECT * FROM places").fetchall()

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            rating = request.form.get("rating", "").strip()
            comment = request.form.get("comment", "").strip()
            place_id = request.form.get("place_id", "").strip()

            errors = []

            if not username:
                errors.append("Имя пользователя обязательно")

            if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
                errors.append("Укажите оценку от 1 до 5")

            if not comment:
                errors.append("Комментарий не может быть пустым")

            if not place_id.isdigit() or conn.execute("SELECT id FROM places WHERE id = ?", (int(place_id),)).fetchone() is None:
                errors.append("Выберите корректное заведение")

            if errors:
                return render_template(
                    "add.html",
                    places=places,
                    errors=errors,
                    username=username,
                    rating=rating,
                    comment=comment,
                    place_id=place_id
                )

            try:
                conn.execute(
                    "INSERT INTO reviews (username, rating, comment, place_id) VALUES (?, ?, ?, ?)",
                    (username, int(rating), comment, int(place_id))
                )
                conn.commit()
            except sqlite3.Error:
                conn.rollback()
                errors.append("Ошибка базы данных при сохранении отзыва")
                return render_template(
                    "add.html",
                    places=places,
                    errors=errors,
                    username=username,
                    rating=rating,
                    comment=comment,
                    place_id=place_id
                )

            return redirect(url_for("index"))

        return render_template("add.html", places=places)
    except sqlite3.Error:
        return "Ошибка при обращении к базе данных", 500
    finally:
        conn.close()


@app.route("/reviews/<int:review_id>/edit", methods=["GET", "POST"])
def edit_review(review_id):
    conn = get_db_connection()

    try:
        review = conn.execute(
            "SELECT * FROM reviews WHERE id = ?",
            (review_id,)
        ).fetchone()

        if review is None:
            return "Отзыв не найден", 404

        places = conn.execute("SELECT * FROM places").fetchall()

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            rating = request.form.get("rating", "").strip()
            comment = request.form.get("comment", "").strip()
            place_id = request.form.get("place_id", "").strip()

            errors = []

            if not username:
                errors.append("Имя пользователя обязательно")

            if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
                errors.append("Укажите оценку от 1 до 5")

            if not comment:
                errors.append("Комментарий не может быть пустым")

            if not place_id.isdigit() or conn.execute("SELECT id FROM places WHERE id = ?", (int(place_id),)).fetchone() is None:
                errors.append("Выберите корректное заведение")

            if errors:
                return render_template(
                    "edit.html",
                    review=review,
                    places=places,
                    errors=errors,
                    username=username,
                    rating=rating,
                    comment=comment,
                    place_id=place_id
                )

            try:
                conn.execute(
                    "UPDATE reviews SET username = ?, rating = ?, comment = ?, place_id = ? WHERE id = ?",
                    (username, int(rating), comment, int(place_id), review_id)
                )
                conn.commit()
            except sqlite3.Error:
                conn.rollback()
                errors.append("Ошибка базы данных при обновлении отзыва")
                return render_template(
                    "edit.html",
                    review=review,
                    places=places,
                    errors=errors,
                    username=username,
                    rating=rating,
                    comment=comment,
                    place_id=place_id
                )

            return redirect(url_for("detail", review_id=review_id))

        return render_template(
            "edit.html",
            review=review,
            places=places,
            username=review["username"],
            rating=review["rating"],
            comment=review["comment"],
            place_id=review["place_id"]
        )
    except sqlite3.Error:
        return "Ошибка при обращении к базе данных", 500
    finally:
        conn.close()


@app.route("/reviews/<int:review_id>/delete", methods=["POST"])
def delete_review(review_id):
    conn = get_db_connection()

    try:
        review = conn.execute(
            "SELECT id FROM reviews WHERE id = ?",
            (review_id,)
        ).fetchone()

        if review is None:
            return "Отзыв не найден", 404

        conn.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        return "Ошибка базы данных при удалении отзыва", 500
    finally:
        conn.close()

    return redirect(url_for("index"))


@app.route("/stats")
def stats():
    conn = get_db_connection()

    try:
        total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
        avg_rating = conn.execute("SELECT AVG(rating) FROM reviews").fetchone()[0]
        five_stars = conn.execute("SELECT COUNT(*) FROM reviews WHERE rating = 5").fetchone()[0]
    except sqlite3.Error:
        return "Ошибка при получении статистики из базы данных", 500
    finally:
        conn.close()

    if avg_rating is not None:
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0

    return render_template(
        "stats.html",
        total=total_reviews,
        avg=avg_rating,
        five_stars=five_stars
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
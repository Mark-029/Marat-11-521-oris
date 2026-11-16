from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

reviews = [
    {
        "id": 1,
        "username": "Иван",
        "rating": 5,
        "comment": "Всё отлично",
    },
    {
        "id": 2,
        "username": "Анна",
        "rating": 4,
        "comment": "Хорошее место",
    },
    {
        "id": 3,
        "username": "Алексей",
        "rating": 2,
        "comment": "Обслуживание медленное",
    }
]


@app.route("/")
def index():
    rating_filter = request.args.get("rating")

    filtered_reviews = reviews

    if rating_filter and rating_filter.isdigit():
        rating_filter = int(rating_filter)
        filtered_reviews = [r for r in reviews if r["rating"] == rating_filter]

    return render_template("index.html", reviews=filtered_reviews, current_filter=rating_filter)


@app.route("/reviews/<int:review_id>")
def detail(review_id):
    review = None

    for item in reviews:
        if item["id"] == review_id:
            review = item
            break

    if review is None:
        return "Отзыв не найден", 404

    return render_template("detail.html", review=review)


@app.route("/reviews/add", methods=["GET", "POST"])
def add_review():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        rating = request.form.get("rating", "").strip()
        comment = request.form.get("comment", "").strip()

        errors = []

        if not username:
            errors.append("Имя пользователя обязательно")

        if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
            errors.append("Укажите оценку от 1 до 5")

        if not comment:
            errors.append("Комментарий не может быть пустым")

        if errors:
            return render_template("add.html", errors=errors, username=username, rating=rating, comment=comment)

        new_review = {
            "id": len(reviews) + 1,
            "username": username,
            "rating": int(rating),
            "comment": comment,
        }

        reviews.append(new_review)
        return redirect(url_for("index"))

    return render_template("add.html")


@app.route("/reviews/<int:review_id>/edit", methods=["GET", "POST"])
def edit_review(review_id):
    review = None

    for item in reviews:
        if item["id"] == review_id:
            review = item
            break

    if review is None:
        return "Отзыв не найден", 404

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        rating = request.form.get("rating", "").strip()
        comment = request.form.get("comment", "").strip()

        errors = []

        if not username:
            errors.append("Имя пользователя обязательно")

        if not rating or not rating.isdigit() or not (1 <= int(rating) <= 5):
            errors.append("Укажите оценку от 1 до 5")

        if not comment:
            errors.append("Комментарий не может быть пустым")

        if errors:
            return render_template("edit.html", review=review, errors=errors,
                                   username=username, rating=rating, comment=comment)

        review["username"] = username
        review["rating"] = int(rating)
        review["comment"] = comment

        return redirect(url_for("detail", review_id=review["id"]))

    return render_template("edit.html", review=review,
                           username=review["username"],
                           rating=review["rating"],
                           comment=review["comment"])


@app.route("/reviews/<int:review_id>/delete", methods=["POST"])
def delete_review(review_id):
    global reviews

    reviews = [r for r in reviews if r["id"] != review_id]

    return redirect(url_for("index"))


@app.route("/stats")
def stats():
    total_reviews = len(reviews)

    if total_reviews > 0:
        avg_rating = sum(r["rating"] for r in reviews) / total_reviews
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = 0

    five_stars = len([r for r in reviews if r["rating"] == 5])

    return render_template("stats.html",
                           total=total_reviews,
                           avg=avg_rating,
                           five_stars=five_stars)


if __name__ == "__main__":
    app.run(debug=True)
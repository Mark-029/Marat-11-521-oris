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
    return render_template("index.html", reviews=reviews)


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


if __name__ == "__main__":
    app.run(debug=True)
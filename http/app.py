import json
import os
import itertools
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

DATA_FILE = "notes.json"


def load_notes():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []


def save_notes():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)


notes = load_notes()

max_id = max((n["id"] for n in notes), default=0)
note_ids = itertools.count(max_id + 1)


def find_note(note_id):
    return next((n for n in notes if n["id"] == note_id), None)


@app.get("/")
def index():
    return "<h1>Гостевая книга</h1>"


@app.get("/notes")
def list_notes():
    author = request.args.get("author")
    limit_str = request.args.get("limit", "10")
    offset_str = request.args.get("offset", "0")
    sort_by = request.args.get("sort", "id")
    order_by = request.args.get("order", "asc")

    if sort_by not in ("id", "likes"):
        return jsonify(error="sort must be 'id' or 'likes'"), 400
    if order_by not in ("asc", "desc"):
        return jsonify(error="order must be 'asc' or 'desc'"), 400

    try:
        limit = int(limit_str)
        if not (1 <= limit <= 100):
            return jsonify(error="limit must be between 1 and 100"), 400
    except ValueError:
        return jsonify(error="limit must be an integer"), 400

    try:
        offset = int(offset_str)
        if offset < 0:
            return jsonify(error="offset must be >= 0"), 400
    except ValueError:
        return jsonify(error="offset must be an integer"), 400

    result_notes = notes
    if author:
        result_notes = [n for n in result_notes if n["author"] == author]

    is_desc = (order_by == "desc")
    result_notes = sorted(result_notes, key=lambda x: x[sort_by], reverse=is_desc)

    paginated_notes = result_notes[offset: offset + limit]
    return jsonify(paginated_notes)


@app.post("/notes")
def create_note():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="invalid JSON payload"), 400

    text = data.get("text")
    author = data.get("author")

    if not isinstance(text, str) or not text.strip():
        return jsonify(error="field 'text' (non-empty string) is required"), 400
    if not isinstance(author, str) or not author.strip():
        return jsonify(error="field 'author' (non-empty string) is required"), 400

    note = {
        "id": next(note_ids),
        "author": author.strip(),
        "text": text.strip(),
        "likes": 0
    }
    notes.append(note)
    save_notes()
    return jsonify(note), 201


@app.get("/notes/<int:note_id>")
def get_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    return jsonify(note)


@app.put("/notes/<int:note_id>")
def update_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="invalid JSON payload"), 400

    text = data.get("text")
    author = data.get("author")

    if not isinstance(text, str) or not text.strip():
        return jsonify(error="field 'text' (non-empty string) is required"), 400
    if not isinstance(author, str) or not author.strip():
        return jsonify(error="field 'author' (non-empty string) is required"), 400

    note["author"] = author.strip()
    note["text"] = text.strip()
    save_notes()
    return jsonify(note), 200


@app.patch("/notes/<int:note_id>")
def patch_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="invalid JSON payload"), 400

    if "text" in data:
        text = data["text"]
        if not isinstance(text, str) or not text.strip():
            return jsonify(error="field 'text' must be a non-empty string"), 400
        note["text"] = text.strip()

    if "author" in data:
        author = data["author"]
        if not isinstance(author, str) or not author.strip():
            return jsonify(error="field 'author' must be a non-empty string"), 400
        note["author"] = author.strip()

    save_notes()
    return jsonify(note), 200


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)
    notes.remove(note)
    save_notes()
    return "", 204


@app.delete("/notes")
def delete_notes_by_author():
    global notes
    author = request.args.get("author")

    if not author or not author.strip():
        return jsonify(error="query parameter 'author' (non-empty string) is required"), 400

    author_clean = author.strip()
    initial_count = len(notes)

    notes = [n for n in notes if n["author"] != author_clean]
    deleted_count = initial_count - len(notes)

    if deleted_count > 0:
        save_notes()

    return jsonify(deleted=deleted_count), 200


@app.post("/notes/<int:note_id>/like")
def like_note(note_id):
    note = find_note(note_id)
    if note is None:
        abort(404)

    note["likes"] += 1
    save_notes()
    return jsonify(note), 200


@app.get("/authors")
def get_authors_stats():
    if not notes:
        return jsonify([])

    stats = {}
    for note in notes:
        author = note["author"]
        if author not in stats:
            stats[author] = {"author": author, "notes": 0, "likes": 0}
        stats[author]["notes"] += 1
        stats[author]["likes"] += note.get("likes", 0)

    result = sorted(stats.values(), key=lambda x: x["author"])
    return jsonify(result)


@app.errorhandler(404)
def not_found(error):
    return jsonify(error="not found"), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify(error="method not allowed"), 405


if __name__ == "__main__":
    app.run(debug=True)
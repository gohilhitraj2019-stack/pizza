from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask_wtf.csrf import CSRFProtect
import sqlite3
DATABASE = "pizza.db"

SELECT_ALL_PIZZAS = "SELECT * FROM pizza"
SELECT_ALL_REVIEWS = "SELECT * FROM review"
SELECT_ABOUT = "SELECT * FROM about_stats LIMIT 1"
IMAGE_PATH = "static/images/"
app = Flask(__name__)

app.secret_key = "pizza_project_secret_key"
csrf = CSRFProtect(app)


# ---------------- HOME PAGE ----------------

@app.route("/", methods=["GET"])
def home():

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Pizza
        cursor.execute(SELECT_ALL_PIZZAS)
        pizzas = cursor.fetchall()

        # Reviews
        cursor.execute(SELECT_ALL_REVIEWS)
        reviews = cursor.fetchall()

        # About Stats
        cursor.execute(SELECT_ABOUT)
        about = cursor.fetchone()

    return render_template(
        "index.html",
        pizzas=pizzas,
        reviews=reviews,
        about=about
    )

# ---------------- ADMIN LOGIN ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        with sqlite3.connect(DATABASE) as conn:
         cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin:
            return redirect(url_for("dashboard"))
        else:
            return "Invalid Username or Password"

    return render_template("admin_login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET"])
def dashboard():

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()



    cursor.execute(SELECT_ALL_REVIEWS)
    reviews = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM pizza")
    total_pizzas = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(price) FROM pizza")
    average_price = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(price) FROM pizza")
    total_value = cursor.fetchone()[0] or 0

    cursor.execute(SELECT_ABOUT) 
    about = cursor.fetchone()                             
    conn.close()

    return render_template(
        "dashboard.html",
        reviews=reviews,
        total_pizzas=total_pizzas,
        average_price=round(average_price, 2),
        total_value=total_value,
        about=about                                    
    )
# ---------------- ADD PIZZA ----------------

@app.route("/addpizza", methods=["GET", "POST"])
def addpizza():

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]

        image = request.files["image"]
        filename = secure_filename(image.filename)

        image.save(IMAGE_PATH + filename)

        with sqlite3.connect(DATABASE) as conn:
         cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pizza(name, description, price, image)
            VALUES (?, ?, ?, ?)
        """, (name, description, price, filename))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_pizza.html")
# ---------------- EDIT PIZZA ----------------
@app.route("/editpizza/<int:id>", methods=["GET", "POST"])
def editpizza(id):

    with sqlite3.connect(DATABASE) as conn:
      cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]

        image = request.files["image"]
        filename = secure_filename(image.filename)

        if filename != "":
            image.save(IMAGE_PATH + filename)
        else:
            cursor.execute("SELECT image FROM pizza WHERE id=?", (id,))
            filename = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE pizza
            SET name=?, description=?, price=?, image=?
            WHERE id=?
        """, (name, description, price, filename, id))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM pizza WHERE id=?", (id,))
    pizza = cursor.fetchone()

    conn.close()

    return render_template("edit_pizza.html", pizza=pizza)
# ---------------- DELETE  PIZZA ----------------

@app.route("/deletepizza/<int:id>", methods=["GET"])
def deletepizza(id):

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute("DELETE FROM pizza WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- REVIEW DASHBOARD ----------------

@app.route("/reviews", methods=["GET"])
def reviews():

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()
    cursor.execute(SELECT_ALL_REVIEWS)
    reviews = cursor.fetchall()

    conn.close()

    return render_template("review_dashboard.html", reviews=reviews)   
 # ---------------- ADD REVIEW ----------------

@app.route("/addreview", methods=["GET", "POST"])
def addreview():

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        rating = request.form["rating"]
        review = request.form["review"]

        # Image Upload
        image = request.files["image"]
        filename = secure_filename(image.filename)

        image.save(IMAGE_PATH + filename)

        with sqlite3.connect(DATABASE) as conn:
         cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO review(customer_name, image, rating, review)
            VALUES (?, ?, ?, ?)
        """, (customer_name, filename, rating, review))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_review.html")
# ---------------- EDIT REVIEW ----------------

@app.route("/editreview/<int:id>", methods=["GET", "POST"])
def editreview(id):

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        rating = request.form["rating"]
        review = request.form["review"]

        image = request.files["image"]
        filename = secure_filename(image.filename)

        if filename != "":
            image.save(IMAGE_PATH + filename)
        else:
            cursor.execute("SELECT image FROM review WHERE id=?", (id,))
            filename = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE review
            SET customer_name=?, image=?, rating=?, review=?
            WHERE id=?
        """, (customer_name, filename, rating, review, id))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    cursor.execute("SELECT * FROM review WHERE id=?", (id,))
    review = cursor.fetchone()

    conn.close()

    return render_template("edit_review.html", review=review)
# ---------------- DELETE REVIEW ----------------

@app.route("/deletereview/<int:id>", methods=["GET"])
def deletereview(id):

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute("DELETE FROM review WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route("/search", methods=["GET"])
def search():

    keyword = request.args.get("q", "")

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM pizza WHERE name LIKE ?",
        ('%' + keyword + '%',)
    )

    pizzas = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM pizza")
    total_pizzas = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(price) FROM pizza")
    average_price = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(price) FROM pizza")
    total_value = cursor.fetchone()[0] or 0

    conn.close()

    return render_template(
        "dashboard.html",
        pizzas=pizzas,
        total_pizzas=total_pizzas,
        average_price=round(average_price, 2),
        total_value=total_value
    )
@app.route("/logout", methods=["GET"])
def logout():
    return redirect(url_for("admin"))

# ---------------- DB SETUP (About Stats) ----------------

def init_about_stats():
    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS about_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            years_experience TEXT NOT NULL,
            happy_customers TEXT NOT NULL,
            pizza_recipes TEXT NOT NULL,
            fast_delivery TEXT NOT NULL
        )
    ''')

    # Seed one row only if table is empty
    cursor.execute("SELECT COUNT(*) FROM about_stats")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO about_stats
            (description, years_experience, happy_customers, pizza_recipes, fast_delivery)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            "Pizza Paradise has been serving delicious pizzas made with fresh ingredients and authentic Italian recipes. Our mission is to provide high-quality food with excellent customer service.",
            "10+", "50K+", "100+", "24/7"
        ))

    conn.commit()
    conn.close()


init_about_stats()  # runs once when the app starts

# ---------------- EDIT ABOUT STATS ----------------
@app.route("/editabout", methods=["GET", "POST"])
def editabout():
    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    if request.method == "POST":

        description = request.form["description"]
        years_experience = request.form["years_experience"]
        happy_customers = request.form["happy_customers"]
        pizza_recipes = request.form["pizza_recipes"]
        fast_delivery = request.form["fast_delivery"]

        cursor.execute("""
            UPDATE about_stats
            SET description=?, years_experience=?, happy_customers=?, pizza_recipes=?, fast_delivery=?
            WHERE id=1
        """, (description, years_experience, happy_customers, pizza_recipes, fast_delivery))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    cursor.execute(SELECT_ABOUT)
    about = cursor.fetchone()

    conn.close()

    return render_template("edit_about.html", about=about)


# ----------------API----------------

@app.route("/api/pizzas", methods=["GET"])
def get_pizzas():
    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute(SELECT_ALL_PIZZAS)
    rows = cursor.fetchall()

    pizzas = []

    for row in rows:
        pizzas.append({
            "id": row[0],
            "description": row[2],
            "name": row[1],
            "price": row[3],
            "image": row[4]  
        })

    conn.close()

    return jsonify(pizzas)

# ----------------API ID----------------
@app.route("/api/pizzas/<int:pizza_id>", methods=["GET"])
def get_pizza(pizza_id):

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute("SELECT * FROM pizza WHERE id = ?", (pizza_id,))
    pizza = cursor.fetchone()

    conn.close()

    if pizza:
       return jsonify({
    "id": pizza[0],
    "name": pizza[1],
    "description": pizza[2],
    "price": pizza[3],
    "image": pizza[4]
})

    return jsonify({
        "message": "Pizza not found"
    }), 404


# ----------------API REVIEW ----------------

@app.route("/api/review", methods=["GET"])
def get_reviews():

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute(SELECT_ALL_REVIEWS)
    reviews = cursor.fetchall()

    conn.close()

    review_list = []

    for review in reviews:
       review_list.append({
    "id": review[0],
    "customer_name": review[1],
    "image": review[2],
    "rating": review[3],
    "review": review[4]
})
    return jsonify(review_list)


# ----------------API REVIEW ID ----------------

@app.route("/api/review/<int:review_id>", methods=["GET"])
def get_review(review_id):

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute("SELECT * FROM review WHERE id = ?", (review_id,))
    review = cursor.fetchone()

    conn.close()

    if review:
        return jsonify({
    "id": review[0],
    "customer_name": review[1],
    "image": review[2],
    "rating": review[3],
    "review": review[4]
})

    return jsonify({
        "message": "review not found"
    }), 404


# ----------------API LOGIN USERNAME,PASS----------------


@app.route("/api/admin", methods=["GET"])
def get_admin():

    with sqlite3.connect(DATABASE) as conn:
     cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin")
    admin = cursor.fetchone()

    conn.close()

    if admin:
       return jsonify({
    "id": admin[0],
    "password": admin[2],
    "username": admin[1]
})
    return jsonify({"message": "Admin not found"}), 404

# ----------------API ABOUT US ----------------


@app.route("/api/aboutus", methods=["GET"])
def about_stats():

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM about_stats")
        about = cursor.fetchone()

    if about:
        return jsonify({
            "description": about[1],
            "years_experience": about[2],
            "happy_customers": about[3],
            "pizza_recipes": about[4],
            "fast_delivery": about[5]
        })

    return jsonify({"message": "about section not found"}), 404
# ---------------- RUN APP ----------------

if __name__ == "__main__":
 app.run(port=5001)
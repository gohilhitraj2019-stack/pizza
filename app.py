from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)


# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    # Pizza
    cursor.execute("SELECT * FROM pizza")
    pizzas = cursor.fetchall()

    # Reviews
    cursor.execute("SELECT * FROM review")
    reviews = cursor.fetchall()

    # About Stats
    cursor.execute("SELECT * FROM about_stats LIMIT 1")
    about = cursor.fetchone()

    conn.close()

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

        conn = sqlite3.connect("pizza.db")
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
@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()



    cursor.execute("SELECT * FROM review")
    reviews = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM pizza")
    total_pizzas = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(price) FROM pizza")
    average_price = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(price) FROM pizza")
    total_value = cursor.fetchone()[0] or 0

    cursor.execute("SELECT * FROM about_stats LIMIT 1")   
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
        filename = image.filename

        image.save("static/images/" + filename)

        conn = sqlite3.connect("pizza.db")
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

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]

        image = request.files["image"]
        filename = image.filename

        if filename != "":
            image.save("static/images/" + filename)
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

@app.route("/deletepizza/<int:id>")
def deletepizza(id):

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pizza WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- REVIEW DASHBOARD ----------------

@app.route("/reviews")
def reviews():

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM review")
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
        filename = image.filename

        image.save("static/images/" + filename)

        conn = sqlite3.connect("pizza.db")
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

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    if request.method == "POST":

        customer_name = request.form["customer_name"]
        rating = request.form["rating"]
        review = request.form["review"]

        image = request.files["image"]
        filename = image.filename

        if filename != "":
            image.save("static/images/" + filename)
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

@app.route("/deletereview/<int:id>")
def deletereview(id):

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM review WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))

@app.route("/search")
def search():

    keyword = request.args.get("q", "")

    conn = sqlite3.connect("pizza.db")
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
@app.route("/logout")
def logout():
    return redirect(url_for("admin"))

# ---------------- DB SETUP (About Stats) ----------------

def init_about_stats():
    conn = sqlite3.connect("pizza.db")
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

    conn = sqlite3.connect("pizza.db")
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

    cursor.execute("SELECT * FROM about_stats LIMIT 1")
    about = cursor.fetchone()

    conn.close()

    return render_template("edit_about.html", about=about)


# ----------------API----------------

@app.route("/api/pizzas", methods=["GET"])
def get_pizzas():
    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pizza")
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

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pizza WHERE id = ?", (pizza_id,))
    pizza = cursor.fetchone()

    conn.close()

    if pizza:
        return jsonify({
            "id": pizza[1],
            "description": pizza[0],
            "name": pizza[3],
            "price": pizza[2],
        })

    return jsonify({
        "message": "Pizza not found"
    }), 404


# ----------------API REVIEW ----------------

@app.route("/api/review", methods=["GET"])
def get_reviews():

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM review")
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

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM review WHERE id = ?", (review_id,))
    review = cursor.fetchone()

    conn.close()

    if review:
        return jsonify({
            "id": review[0],
            "name": review[1],
            "rating": review[2],
            "review": review[3],
        })

    return jsonify({
        "message": "review not found"
    }), 404


# ----------------API LOGIN USERNAME,PASS----------------


@app.route("/api/admin", methods=["GET"])
def get_admin():

    conn = sqlite3.connect("pizza.db")
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

    conn = sqlite3.connect("pizza.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM about_stats")
    about = cursor.fetchone()

    conn.close()

    if about:
     return jsonify({
    "description": about[1],
    "happy_customers": about[3],
    "years_experience": about[2],
    "pizza_recipes": about[4],
    "fast_delivery": about[5]
})
    return jsonify({"message": "about section not found"}), 404

# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)

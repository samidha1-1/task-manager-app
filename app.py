from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "3aa7b16253eb2885c5ad6d5cf89dfbd02507335701bb2b3140ea319eb0a39178"


# -------------------------
# MySQL Connection
# -------------------------

import os

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3307")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root123"),
        database=os.getenv("DB_NAME", "task_manager")
    )


# -------------------------
# Home
# -------------------------

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


# -------------------------
# Register
# -------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users (username, email, password)
                VALUES (%s, %s, %s)
                """,
                (username, email, hashed_password)
            )

            db.commit()

            flash("Registration successful. Please login.", "success")

            return redirect(url_for("login"))

        except mysql.connector.Error as error:

            flash("Email already exists.", "danger")

        finally:

            cursor.close()
            db.close()

    return render_template("register.html")


# -------------------------
# Login
# -------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM users WHERE email = %s",
            (email,)
        )

        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


# -------------------------
# Dashboard
# -------------------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM tasks
        WHERE user_id = %s
        ORDER BY created_at DESC
        """,
        (session["user_id"],)
    )

    tasks = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        tasks=tasks
    )


# -------------------------
# Add Task
# -------------------------

@app.route("/add-task", methods=["POST"])
def add_task():

    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form["title"]
    description = request.form["description"]

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (user_id, title, description)
        VALUES (%s, %s, %s)
        """,
        (
            session["user_id"],
            title,
            description
        )
    )

    db.commit()

    cursor.close()
    db.close()

    flash("Task added successfully.", "success")

    return redirect(url_for("dashboard"))


# -------------------------
# Complete Task
# -------------------------

@app.route("/complete/<int:task_id>")
def complete_task(task_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET completed = 1
        WHERE id = %s AND user_id = %s
        """,
        (task_id, session["user_id"])
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("dashboard"))


# -------------------------
# Delete Task
# -------------------------

@app.route("/delete/<int:task_id>")
def delete_task(task_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = %s AND user_id = %s
        """,
        (task_id, session["user_id"])
    )

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("dashboard"))


# -------------------------
# Logout
# -------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
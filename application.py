import os
import math
import requests
import urllib.parse

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
import datetime

# import schedule
import time

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
# app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///ingredients.db")

@app.route("/")
@login_required
def index():

    if request.method == "GET":
        # sending in all order data from database
        today = datetime.date.today()
        total_requests = db.execute("SELECT * from requests where date=:date", date = today)
        requests = db.execute("SELECT * from requests where user_id = :id and date=:date",id = session["user_id"], date=today)
        date = datetime.date.today() + datetime.timedelta(days=1)

    return render_template("index.html", date=date, requests=requests, total_requests=total_requests)


@app.route("/order", methods=["GET", "POST"])
@login_required
def order():
    if request.method == "GET":
        # sends in all acceptable dining locations
        location = request.form.get("location_id")
        response = requests.get(f"https://api.cs50.io/dining/locations")
        response.raise_for_status()
        locations = response.json()
        halls = []
        for item in locations:
            halls.append(item["name"])
        return render_template("order.html", halls=halls)

    if request.method == "POST":

        meal = request.form.get("meal_id")

        location = request.form.get("location_id").lower()
        response = requests.get(f"https://api.cs50.io/dining/locations")
        response.raise_for_status()
        locations = response.json()
        halls = []
        for item in locations:
            item["name"] = item["name"].lower()
            halls.append(item["name"].lower())
        match = False
        hall_id = 0

        # checking if location is valid
        for place in locations:
            if location in place["name"]:
                match = True
                hall_id = place["id"]
        if not match:
            return apology("Enter valid location")

        # using helpers.py, API will find all food items for this particular dining hall and meal time
        menu = lookup(str(hall_id), str(meal))

        items = []

        # create list of items to be sent to html page
        for item in menu:
            item=str(item)
            response = requests.get(f"https://api.cs50.io/dining/recipes/{urllib.parse.quote_plus(item)}")
            response.raise_for_status()
            recipe = response.json()

            items.append(recipe["name"])

        session["items"] = items
        session["location"] = location
        session["meal"] = meal
        return render_template("menu.html", items=session["items"])


@app.route("/menu", methods=["GET", "POST"])
@login_required
def menu():

    quantity = 0
    if request.method == "GET":
        return render_template("/menu", menu=session["menu"])

    if request.method == "POST":
        date = datetime.date.today()
        item = request.form.get("item")
        quantity = request.form.get("quantity")

        # inserts users input into table
        db.execute("INSERT into requests (user_id, location, meal, item, quantity, date) VALUES (:user_id, :location, :meal, :item, :quantity, :date)", user_id=session["user_id"], location=session["location"], meal=session["meal"], item=item, quantity=quantity, date=date)
        return render_template("menu.html", item=item, quantity=quantity, items=session["items"])

@app.route("/total", methods=["GET"])
@login_required
def total():

    if request.method == "GET":
        items = db.execute("SELECT * from requests GROUP BY item")
        return render_template("total.html", items=items)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # elif not request.form.get("house"):
        #     return apology("must provide dining location", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    else:
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        if not request.form.get("house"):
            return apology("must provide your dining location", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Password does not match", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 0:
            return apology("Username already taken", 403)

        username = request.form.get("username")
        location = request.form.get("house")
        password = request.form.get("password")

        # get id of house
        if location == "Lowell" or location == "Winthrop":
            location = "Lowell and Winthrop House"
        if location == "Eliot" or location == "Kirkland":
            location = "Eliot and Kirkland House"
        if location == "Cabot" or location == "Pforzheimer":
            location = "Cabot and Pforzheimer"
        if location == "Dunster" or location == "Mather":
            location = "Dunster and Mather House"

        response = requests.get(f"https://api.cs50.io/dining/locations")
        response.raise_for_status()
        locations = response.json()
        match = False
        hall_id = 0

        # check for valid location
        for place in locations:
            if place["name"] == location:
                match = True
                hall_id = place["id"]
        if not match:
            return apology("Enter valid location")

        password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, location, hash) VALUES (:username, :location, :hash)", username = username, location = hall_id, hash = password)

    return redirect("/login")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

import os
import requests
import urllib.parse

import datetime
from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(location, meal):
    """Look up quote for symbol."""

    # get tomorrow's date
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(1)
    tomrrow = datetime.datetime.strftime(tomorrow,'%Y-%m-%d')
    # Contact API
    try:
        response = requests.get(f"https://api.cs50.io/dining/menus?date={tomrrow}&meal={urllib.parse.quote_plus(meal)}&location={urllib.parse.quote_plus(location)}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        # will return a list of dicts which includes recipe id
        quote = response.json()
        recipe_dict = []
        for item in quote:
            recipe_dict.append(item["recipe"])
        return recipe_dict
        # {
        #     "item": quote["recipe"],
        #     "meal": quote["meal"],
        #     "location": quote["location"]
        #     # "date": quote["date"]
        # }
    except (KeyError, TypeError, ValueError):
        return None

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

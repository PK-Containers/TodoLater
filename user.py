from werkzeug.exceptions import NotFound
from flask import Flask, jsonify, make_response
import requests
import os
import simplejson as json

app = Flask(__name__)

database_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print database_path

with open("{}/app/database/users.json".format(database_path), "r") as f:
    users = json.load(f)

@app.route("/", methods=['GET'])
def hello():
    return jsonify({
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<username>",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    })


@app.route("/users", methods=['GET'])
def users_list():
    return jsonify(users)


@app.route("/users/<username>", methods=['GET'])
def user_record(username):
    if username not in users:
        return  "Not Found"

    return jsonify(users[username])


@app.route("/users/<username>/bookings", methods=['GET'])
def user_bookings(username):
    """
    Gets booking information from the 'Bookings Service' for the user, and
     movie ratings etc. from the 'Movie Service' and returns a list.
    :param username:
    :return: List of Users bookings
    """
    if username not in users:
        return "User '{}' not found.".format(username)
        
    try:
        users_bookings = requests.get("http://127.0.0.1:5003/bookings/{}".format(username))
    except requests.exceptions.ConnectionError:
        return ServiceUnavailable("The Bookings service is unavailable.")

    if users_bookings.status_code == 404:
        return "No bookings were found for {}".format(username)

    users_bookings = users_bookings.json()

    # For each booking, get the rating and the movie title
    result = {}
    for date, movies in users_bookings.iteritems():
        result[date] = []
        for movieid in movies:
            try:
                movies_resp = requests.get("http://127.0.0.1:5001/movies/{}".format(movieid))
            except requests.exceptions.ConnectionError:
                return ServiceUnavailable("The Movie service is unavailable.")
            movies_resp = movies_resp.json()
            result[date].append({
                "title": movies_resp["title"],
                "rating": movies_resp["rating"],
                "uri": movies_resp["uri"]
            })

    return jsonify(result)


@app.route("/users/<username>/suggested", methods=['GET'])
def user_suggested(username):
    """
    Returns movie suggestions. The algorithm returns a list of 3 top ranked
    movies that the user has not yet booked.
    :param username:
    :return: Suggested movies
    """
    return "Not implemented"


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002, debug=True)

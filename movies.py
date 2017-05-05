from werkzeug.exceptions import NotFound
from flask import Flask, jsonify, make_response
import requests
import os
import simplejson as json

app = Flask(__name__)

database_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print database_path

with open("{}/app/database/movies.json".format(database_path), "r") as f:
    movies = json.load(f)

@app.route("/", methods=['GET'])
def hello():
    return jsonify({
        "uri": "/",
        "subresource_uris": {
            "movies": "/movies",
            "movie": "/movies/<id>"
        }
    })

@app.route("/movies/<movieid>", methods=['GET'])
def movie_info(movieid):
    if movieid not in movies:
        return "Not Found"

    result = movies[movieid]
    result["uri"] = "/movies/{}".format(movieid)

    return jsonify(result)


@app.route("/movies", methods=['GET'])
def movie_record():
    return jsonify(movies)


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5002, debug=True)

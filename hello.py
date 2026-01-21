from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify
import atexit
import os
import json

app = Flask(__name__, static_url_path="")

db_name = "mydb"

client = Cloudant(
    os.environ["COUCHDB_USER"],
    os.environ["COUCHDB_PASSWORD"],
    url=os.getenv(
        "COUCHDB_URL", "http://{}:5984".format(os.getenv("COUCHDB_HOST", "localhost")),
    ),
    connect=True,
)
db = client.create_database(db_name, throw_on_exists=False)

port = int(os.getenv("PORT", 8000))


@app.route("/")
def root():
    return app.send_static_file("index.html")


# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */
@app.route("/api/visitors", methods=["GET"])
def get_visitor():
    if client:
        return jsonify(list(map(lambda doc: doc["name"], db)))
    else:
        print("No database")
        return jsonify([])


# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */
@app.route("/api/visitors", methods=["POST"])
def put_visitor():
    user = request.json["name"]
    data = {"name": user}
    if client:
        my_document = db.create_document(data)
        data["_id"] = my_document["_id"]
        return jsonify(data)
    else:
        print("No database")
        return jsonify(data)


@atexit.register
def shutdown():
    if client:
        client.disconnect()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)

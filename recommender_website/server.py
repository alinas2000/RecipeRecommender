from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


import recommender as r

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret!'
socketio = SocketIO(app)


@app.route("/")
def process():
    to_rate = r.recipes.sample(5)[["name", "recipe_id"]]

    return render_template("see_results.html", recipes=to_rate.values.tolist())


@socketio.on("get_recommendations")
def create_recommendations(json):
    prefs = {i['name']: i['value'] for i in json}
    print(prefs)
    results = r.recommend(prefs, progress_func=lambda x: emit("progress", x))
    emit("recommendations", results)


if __name__ == "__main__":
    socketio.run(app, debug=True)

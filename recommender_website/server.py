from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


import recommender as r

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret!'
socketio = SocketIO(app)


@app.route("/")
def process():
    to_rate = r.recipes.sample(5)[["name", "recipe_id", "description"]]

    return render_template("see_results.html", recipes=to_rate.values.tolist())


@app.route("/recipes/<number>")
def serve_recipe(number):
    number = int(number)
    return render_template(
        "recipe.html",
        recipe_name=r.get_recipe_by_id(number, "name"),
        recipe_description=r.get_recipe_by_id(number, "description"),
        recipe_steps=r.get_recipe_by_id(number, "steps")
    )


@socketio.on("get_recommendations")
def create_recommendations(json):
    prefs = {i['name']: i['value'] for i in json}
    print(prefs)
    results = r.recommend(prefs, progress_func=lambda x: emit("progress", x))
    emit("recommendations", [{"name": r.get_recipe_by_id(
        i[0], "name"), "id":i[0], "est_rating": i[1]} for i in results[:20]])


if __name__ == "__main__":
    socketio.run(app, debug=True)

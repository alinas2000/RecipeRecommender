#define dictionary of labels to ingredient names

ingredient_dict = {
    0: "apple",
    1: "avocado",
    2: "banana",
    3: "beef",
    4: "bellpeppers",
    5: "bread",
    6: "broccoli",
    7: "cabbage",
    8: "cheese",
    9: "chicken",
    10: "corn",
    11: "cucumber",
    12: "egg",
    13: "eggplant",
    14: "greenbeans",
    15: "lemon",
    16: "lettuce",
    17: "mushroom",
    18: "olives",
    19: "onions",
    20: "pasta",
    21: "potatoes",
    22: "rice",
    23: "salmon",
    24: "spinach",
    25: "tomato",

}

ingredient_id_map = {
    "apple": 150,
    "avocado": 255,
    "banana": 342,
    "beef": 422,
    4: "bellpeppers",
    "bread": 715,
    "broccoli": 756,
    "cabbage": 893,
    "cheese": 1170,
    "chicken": 1240,
    "corn": 1803,
    "cucumber": 2001,
    "egg": 2499,
    "eggplant": 2516,
    "greenbeans": 3398,
    "lemon": 4231,
    "lettuce": 4308,
    "mushroom": 4863,
    "olives": 5003,
    "onions": 5010,
    20: "pasta",
    "potatoes": 5648,
    "rice": 6261,
    "salmon": 6260,
    "spinach": 6754,
    "tomato": 7213,

}


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit


import recommender as r


from flask_session.__init__ import Session

from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import os
import pickle
import glob
import pandas as pd
import torch, torchvision
from torch import nn, optim
from torchvision import datasets, models, transforms

device = torch.device('cpu')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret!'
socketio = SocketIO(app)

infile = open('ingredient_classifier_torch.pkl', 'rb')
model = torch.load(infile, map_location=torch.device('cpu'))
infile.close()

app.config["image_uploads"] = 'image-uploads/sample'


@app.route('/', methods=['GET','POST'])
def upload_image():
    files = glob.glob('./image-uploads/sample/*')
    for f in files:
        os.remove(f)

    os.makedirs("./image-uploads/sample", exist_ok=True)
    if request.method == "POST":
        #if request.files:
            images = request.files.getlist("image[]")

            for i in images:
              filename = secure_filename(i.filename)
              path = os.path.join(app.config["image_uploads"], filename)
              i.save(path)

            xform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
            inputs = datasets.ImageFolder('./image-uploads', transform=xform)
            loader = torch.utils.data.DataLoader(inputs, batch_size = len(images), shuffle=True)
            model.eval()
            print("breakpoint")
            with torch.no_grad():
              for samples,_ in loader:
                samples = samples.to(device)
                outs = model(samples)
                _, preds = torch.max(outs.detach(), 1)
            
            preds_list = preds.tolist()
            
            ingredients_list = []

            for p in preds_list:
                ingredients_list.append(ingredient_id_map[ingredient_dict[p]])



            return render_template("output_prediction.html", ingredients=ingredients_list)

    return render_template("uploadImage.html")

@app.route("/rec")
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

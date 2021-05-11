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

#from flask_ngrok import run_with_ngrok

from flask_session.__init__ import Session

from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.utils import secure_filename
import os
import pickle
import glob
import torch, torchvision
from torch import nn, optim
from torchvision import datasets, models, transforms

device = torch.device('cpu')

app = Flask(__name__)
#model = torch.nn.Module.load_state_dict(torch.load('ingredient_classifier.pkl', map_location=torch.device('cpu')))
#torch.load('ingredient_classifier.pkl', map_location=torch.device("cpu"))



infile = open('ingredient_classifier.pkl', 'rb')
model = pickle.load(infile)
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
            image = request.files["image"]
            filename = secure_filename(image.filename)
            path = os.path.join(app.config["image_uploads"], filename)
            image.save(path)
            xform = transforms.Compose([transforms.Resize((224,224)), transforms.ToTensor()])
            inputs = datasets.ImageFolder('./image-uploads', transform=xform)
            loader = torch.utils.data.DataLoader(inputs, batch_size = 4, shuffle=True)
            model.eval()
            with torch.no_grad():
              for samples,_ in loader:
                samples = samples.to(device)
                outs = model(samples)
                _, preds = torch.max(outs.detach(), 1)
            
            preds_list = preds.tolist()
            #for p in preds_list:
            #  print(p)
            print(ingredient_dict[preds_list[0]])
            print("finished")
            return render_template("output_prediction.html", ingredient=ingredient_dict[preds_list[0]])

    return render_template("uploadImage.html")

@app.route('/output_prediction/<i>')
def output_prediction(i):
  return render_template("output_prediction.html", ingredient=i)

#app.run()
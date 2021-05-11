from flask import Flask, send_file, make_response, request, render_template
import string, copy

app = Flask(__name__)

quesSet = {
    'shrimp and potato tapas':['1','2','3','4','5'],
    'creamy chicken black bean tacos':['1','2','3','4','5'],
    'creamy cajun chicken pasta':['1','2','3','4','5'],
    'kittencal\'s italian melt in your mouth meatballs':['1','2','3','4','5'],
    'arroz pilaf':['1','2','3','4','5'],
    'japanese mum\'s chicken':['1','2','3','4','5'],
}

questions = copy.deepcopy(quesSet)

@app.route("/")
def rate():
    return render_template('main.html', q = questions.keys(), o = questions)

@app.route("/result", methods = ["POST"])
def result():
    answer = request.form.to_dict()
    rate = {
        '27208': 0, 
        '89204': 0,
        '39087': 0,
        '69173': 0,
        '22782': 0,
        '68955': 0
        }
    rate['27208'] = int(answer['shrimp and potato tapas'])
    rate['89204'] = int(answer['creamy chicken black bean tacos'])
    rate['39087'] = int(answer['creamy cajun chicken pasta'])
    rate['69173'] = int(answer['kittencal\'s italian melt in your mouth meatballs'])
    rate['22782'] = int(answer['arroz pilaf'])
    rate['68955'] = int(answer['japanese mum\'s chicken'])
#    for i in questions.keys():
#        index = int(i)
#        rate[index] = request.form[i]
    return '<h1>Your Answer: <u>'+ str(rate) +'</u></h1>'

if __name__ == '__main__':
    app.run(debug=True)

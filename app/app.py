from flask import Flask, render_template, redirect, request, url_for
from article import Summarizer
import gunicorn
import shelve
from werkzeug.utils import secure_filename

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("index.html")

@app.route('/news')
def news():
    news_db = shelve.open('news')
    #news_db.clear()
    return render_template("news.html", articles=news_db['data'])

@app.route('/results', methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        text = request.form['text']
        percent = request.form['percent']
        if request.files['upload']:
            file = request.files['upload']
            file.filename = secure_filename(file.filename) # don't know if this is necessary since files aren't stored
            text = file.read().decode("utf-8") # overrides text field input (change?)


        #catches empty inputs
        if not text:
            return render_template('index.html', errormsg="Please enter text, a link, or upload a file")
        if not percent:
            return render_template('index.html', errormsg="Please enter a reduction percentage")

        # catches empty percent field
        if percent.isnumeric():
            percent = int(percent) / 100
        else:
            percent = None
        summary = Summarizer(text)
        summary_text = summary.condense(percent)
        metrics = summary.condense_metrics(summary_text)
        summary_sentences = [sentence.strip() for sentence in summary_text.split('\n')]
        return render_template('results.html', summary_sentences=summary_sentences, metrics=metrics)
    else:
        return render_template('index.html')


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    # note that we set the 404 status explicitly
    return render_template('500.html'), 500



if __name__ == '__main__':
   app.run(host='0.0.0.0', debug=True)

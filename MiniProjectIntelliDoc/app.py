from flask import Flask, render_template, request
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'


if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route("/")
def home():
    return render_template("upload.html")


if __name__ == "__main__":
    app.run(debug=True)
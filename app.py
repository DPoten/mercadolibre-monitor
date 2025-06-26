from flask import Flask, render_template, request, redirect, url_for
import threading
import json
import time
from monitor import start_monitoring, stop_monitoring, add_url, remove_url, get_urls

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", urls=get_urls())

@app.route("/add", methods=["POST"])
def add():
    url = request.form.get("url")
    if url:
        add_url(url)
    return redirect(url_for("index"))

@app.route("/remove/<int:index>")
def remove(index):
    remove_url(index)
    return redirect(url_for("index"))

if __name__ == "__main__":
    start_monitoring()
    try:
        app.run(debug=True, host="0.0.0.0", port=5000)
    finally:
        stop_monitoring()

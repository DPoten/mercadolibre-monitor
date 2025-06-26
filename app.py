from flask import Flask, render_template, request, redirect, url_for
import threading
import re
from monitor import start_monitoring, stop_monitoring, add_url, remove_url, get_urls

app = Flask(__name__)

def clean_url(url):
    # Extract base MercadoLibre product URL without query or fragment
    m = re.match(r"(https://articulo\.mercadolibre\.com\.ar/MLA-\d+[-\w]*)", url)
    if m:
        return m.group(1)
    return url  # fallback

@app.route("/")
def index():
    return render_template("index.html", urls=get_urls())

@app.route("/add", methods=["POST"])
def add():
    raw_url = request.form.get("url")
    if raw_url:
        url = clean_url(raw_url)
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

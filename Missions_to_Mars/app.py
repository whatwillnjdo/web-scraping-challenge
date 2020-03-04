from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars
import os

#Flask set up
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_mission"
mongo = PyMongo(app)

@app.route("/")
def index():
    all_content = mongo.db.all_content.find_one()
    return render_template("index.html", all_content=all_content)


@app.route("/scrape")
def scrape():
    all_content = mongo.db.all_content
    all_content_data = scrape_mars.scrape()
    
    all_content.update({}, all_content_data, upsert=True)
    
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)
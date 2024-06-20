"""This API is to be of use for those who wish to retrieve useful information from our database of earthquake data.
Whether it be an amateur developer or a seasoned researcher, this service should be easy to make the most out of through its endpoints."""
from dotenv import load_dotenv
from flask import Flask, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def endpoint_index():
    return {"message": "Welcome! This is Team Poseidon's API, connected to our Earthquake database. Use this to retrieve information on the earthquake data we have collected."}


if __name__ == "__main__":

    load_dotenv()
    app.run(debug=True, host="0.0.0.0", port=5000)

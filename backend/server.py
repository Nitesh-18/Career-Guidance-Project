from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import pickle
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
app.config["MONGO_URI"] = (
    "mongodb://localhost:27017/NGC"  # Update with your MongoDB URI
)
mongo = PyMongo(app)

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv('JWT_SECRET_KEY', 'fallback_secret_key')  # Fallback if env var is not set
jwt = JWTManager(app)

# Bcrypt for password hashing
bcrypt = Bcrypt(app)

# Load the SVM model and feature selector
MODEL_PATH = "models/svm_model_with_fs.pickle"

with open(MODEL_PATH, "rb") as f:
    clf_svm_fs_loaded, fs_loaded = pickle.load(f)

# Define a mapping for school_type
school_type_mapping = {"Public": 0, "Private": 1}


# User Registration Route
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    # Check if user already exists
    existing_user = mongo.db.users.find_one({"email": data["email"]})
    if existing_user:
        return jsonify({"message": "User already exists!"}), 400

    # Hash password
    hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    # Create a new user
    new_user = {
        "name": data["name"],
        "email": data["email"],
        "password": hashed_password,
    }
    mongo.db.users.insert_one(new_user)

    # Return success with redirect URL to home page
    return jsonify({"message": "User registered successfully!", "redirectUrl": "/"}), 201


# User Login Route
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    user = mongo.db.users.find_one({"email": data["email"]})

    if user and bcrypt.check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(
            identity={"name": user["name"], "email": user["email"]}
        )
        # Send the token and redirect URL to the home page
        return jsonify({"token": access_token, "redirectUrl": "/"}), 200
    else:
        return jsonify({"message": "Invalid email or password!"}), 401



@app.route("/")
def home():
    return "Welcome to the Resume Parser API!"


@app.route("/upload", methods=["POST"])
def upload_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume = request.files["resume"]
    parsed_data = parse_resume(resume)
    return jsonify(parsed_data)


@app.route("/trending-jobs", methods=["GET"])
def get_trending_jobs():
    try:
        response = requests.get("https://remoteok.io/api")
        if response.status_code == 200:
            jobs = response.json()  # Fetch and parse the JSON data
            return jsonify(jobs)
        else:
            return jsonify({"error": "Failed to fetch jobs"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/questionnaire", methods=["POST"])
def submit_questionnaire():
    try:
        data = request.json

        # Convert school_type to numeric using the mapping
        school_type_numeric = school_type_mapping.get(
            data["school_type"], -1
        )  # -1 for unknown types

        # Include sslc and school_type in the features
        features = [
            data["sslc"],  # SSL score
            school_type_numeric,  # School type (encoded)
            data["no_of_miniprojects"],  # Number of mini projects
            data["coresub_skill"],  # Core subject skill
            data["aptitude_skill"],  # Aptitude skill
            data["programming_skill"],  # Programming skill
            data["abstractthink_skill"],  # Abstract thinking skill
            data["design_skill"],  # Design skill
            data["first_computer"],  # First computer used
            data["first_program"],  # First program written
            data["ds_coding"],  # Data structures coding skill
            data["technology_used"],  # Technology used
            data["sympos_attend"],  # Symposiums attended
            data["sympos_won"],  # Symposiums won
            data["extracurricular"],  # Extracurricular activities
            data["learning_style"],  # Learning style
            data["college_skills"],  # College skills
        ]

        # Convert features to a numpy array
        features_array = np.array([features], dtype=float)  # Ensure float type

        # Transform the features using the loaded feature selector
        features_transformed = fs_loaded.transform(features_array)

        # Make predictions using the trained SVM model
        prediction = clf_svm_fs_loaded.predict(features_transformed)

        # Convert prediction to a standard Python type
        prediction_value = int(prediction[0])  # Convert to int for JSON serialization

        return jsonify({"prediction": prediction_value})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

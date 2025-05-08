from flask import Flask, jsonify, render_template
from carelon import run_login
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')  # Flask will automatically look inside /templates/

@app.route('/start-login', methods=['POST'])
def start_login():
    try:
        run_login()  # Run the automation logic from carelon.py
        return jsonify({"message": "Login and downloads completed successfully!"}), 200
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

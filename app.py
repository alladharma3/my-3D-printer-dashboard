from flask import Flask, jsonify, send_file
from flask_cors import CORS
import random
from threading import Lock
import string

app = Flask(__name__)
CORS(app)

class PrinterSimulator:
    def __init__(self):
        self.is_printing = False
        self.progress = 0
        self.lock = Lock()
        self.history = {"extruder": [], "heater_bed": []}

    def get_status(self):
        with self.lock:
            if self.is_printing:
                self.progress = min(self.progress + random.uniform(0.5, 2), 100)
                status = "Printing" if self.progress < 100 else "Idle"
                if self.progress >= 100:
                    self.is_printing = False
            else:
                status = "Idle"
                self.progress = 0 if self.progress >= 100 else self.progress

            extruder_temp = random.randint(180, 220) if self.is_printing else random.randint(20, 50)
            heater_bed_temp = random.randint(50, 70) if self.is_printing else random.randint(20, 30)

            self.history["extruder"].append(extruder_temp)
            self.history["heater_bed"].append(heater_bed_temp)
            if len(self.history["extruder"]) > 20:
                self.history["extruder"].pop(0)
                self.history["heater_bed"].pop(0)

            return {
                "extruder_temp": extruder_temp,
                "heater_bed_temp": heater_bed_temp,
                "print_progress": round(self.progress, 1),
                "status": status,
                "history": self.history
            }

    def start_printing(self):
        with self.lock:
            if not self.is_printing:
                self.is_printing = True
                self.progress = 0
                return True
            return False

    def stop_printing(self):
        with self.lock:
            self.is_printing = False
            return True

printer = PrinterSimulator()

def generate_random_username():
    return ''.join(random.choices(string.ascii_lowercase, k=8))

@app.route('/api/printer_status', methods=['GET'])
def get_printer_status():
    return jsonify(printer.get_status())

@app.route('/api/start', methods=['POST'])
def start_printing():
    success = printer.start_printing()
    return jsonify({"message": "Printing started" if success else "Already printing"}), 200 if success else 400

@app.route('/api/stop', methods=['POST'])
def stop_printing():
    success = printer.stop_printing()
    return jsonify({"message": "Printing stopped" if success else "Already stopped"}), 200 if success else 400

@app.route('/api/profile', methods=['GET'])
def get_profile():
    username =  "Dharmendra"
    return jsonify({
        "name": f"{username.capitalize()}",
        "email": f"{username}@gmail.com",
        "last_print": f"2025-04-{random.randint(1, 30):02d}"
    })

@app.route('/', methods=['GET'])
def serve_dashboard():
    return send_file('index.html')

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)
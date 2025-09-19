import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
import threading
import serial
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")

@app.route("/")
def index():
    return render_template("index.html")

# Arduinoからの値を別スレッドで読み取り → WebSocketで送信
def read_from_arduino():
    try:
        ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)  # Arduinoのポートに変更
        time.sleep(2)  # ポート安定待ち
        while True:
            line = ser.readline().decode("utf-8").strip()
            if line:
                print("Arduino:", line)
                socketio.emit("sensor_data", {"value": line})
    except Exception as e:
        print("Serial error:", e)

@socketio.on("connect")
def on_connect():
    print("Client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected")

if __name__ == "__main__":
    # Arduino読み取りスレッド起動
    t = threading.Thread(target=read_from_arduino, daemon=True)
    t.start()

    socketio.run(app, host="0.0.0.0", port=5000)

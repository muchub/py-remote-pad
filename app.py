from flask import Flask, render_template, request, abort
from flask_socketio import SocketIO
import pyautogui
import keyboard
import qrcode
from pyngrok import ngrok
import secrets
import string

def generate_token(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

# === Configuration ===
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
ACCESS_TOKEN = generate_token()

# === Routes ===
@app.route('/')
def index():
    token = request.args.get("token")
    if token != ACCESS_TOKEN:
        abort(403)
    return render_template("app.html")

# === Socket events ===
@socketio.on("move")
def handle_move(data):
    dx = data.get("dx", 0)
    dy = data.get("dy", 0)
    pyautogui.moveRel(dx, dy)

@socketio.on("click")
def handle_click(data=None):  # Modified to accept optional parameter
    if data and data.get('double', False):
        pyautogui.doubleClick()
    else:
        pyautogui.click()

@socketio.on("keypress")
def handle_keypress(data):
    key = data.get("key")
    if key == "backspace":
        keyboard.send("backspace")
    elif key == "enter":
        keyboard.send("enter")
    elif key:
        keyboard.write(key)

# === QR Code generation ===
def display_qr(public_url):
    url = f"{public_url}?token={ACCESS_TOKEN}"
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    
    try:
        qr.print_ascii(invert=True)
    except Exception as e:
        print("❌ QR print failed:", e)
        print("✅ URL instead:", url)

# === Start the app ===
if __name__ == "__main__":
    public_url = ngrok.connect(5000, bind_tls=True)
    print("Scan this QR on your mobile phone to access the app:\n")
    display_qr(public_url.public_url)
    socketio.run(app, host="0.0.0.0", port=5000)
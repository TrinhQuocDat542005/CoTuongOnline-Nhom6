from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def new_game():
    return render_template('lobby.html')

@app.route('/board/<string:id>')
def board(id):
    return render_template('game.html')

@app.route('/board', methods=['GET', 'POST'])
def move():
    # Placeholder để các bạn khác không bị lỗi khi gọi API
    return json.dumps({"status": "server_ready"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
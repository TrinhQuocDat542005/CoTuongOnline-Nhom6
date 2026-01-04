# Thư viện
from flask import Flask, render_template, request
import socket
import json

# Định nghĩa IP và PORT
IP = '127.0.0.1'
PORT = 8888
BYTES = 1024

# Tạo instance của ứng dụng Flask
app = Flask(__name__)

# Hàm tiện ích để giao tiếp với server UDP
def send_to_udp_server(data):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(str.encode(data), (IP, PORT))
        server_data, _ = client_socket.recvfrom(BYTES)
        return server_data.decode()
    except Exception as e:
        return f"Lỗi khi giao tiếp với server: {e}"
    finally:
        client_socket.close()

@app.route('/')
def new_game():
    return render_template('lobby.html')

@app.route('/board/<string:id>')
def board(id):
    return render_template('game.html')

@app.route('/board', methods=['GET', 'POST'])
def move():
    if request.method == 'GET':
        user_data = json.dumps(dict(request.args))
    elif request.method == 'POST':
        user_data = json.dumps(dict(request.form))
    
    # Gửi dữ liệu tới server UDP và nhận phản hồi
    response = send_to_udp_server(user_data)
    return response

# Khởi chạy ứng dụng
if __name__ == '__main__':
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)

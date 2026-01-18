# Thư viện
from flask import Flask, render_template, request, jsonify
import socket
import json

# Định nghĩa IP và PORT của UDP Server (Phải khớp với file server.py)
IP = '127.0.0.1'
PORT = 8888
BYTES = 1024

# Tạo instance của ứng dụng Flask
app = Flask(__name__)

# Hàm tiện ích để giao tiếp với server UDP
def send_to_udp_server(data):
    client_socket = None
    try:
        # Tạo socket mới cho mỗi request (Stateless)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Set timeout để tránh treo Web nếu UDP Server chết
        client_socket.settimeout(2) 
        
        client_socket.sendto(str.encode(data), (IP, PORT))
        server_data, _ = client_socket.recvfrom(BYTES)
        return server_data.decode()
    except socket.timeout:
        return json.dumps({"status": "error", "message": "Server UDP không phản hồi"})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Lỗi socket: {str(e)}"})
    finally:
        if client_socket:
            client_socket.close()

@app.route('/')
def new_game():
    return render_template('lobby.html')

@app.route('/board/<string:id>')
def board(id):
    # Truyền ID vào template để JS biết đang chơi bàn nào
    return render_template('game.html', game_id=id) 

@app.route('/board', methods=['GET', 'POST'])
def move():
    user_data_dict = {}

    # 1. Ưu tiên lấy dữ liệu dạng JSON (thường dùng trong AJAX/Fetch)
    if request.is_json:
        user_data_dict = request.get_json()
    # 2. Nếu không có JSON, thử lấy từ Form Data (thẻ <form>)
    elif request.form:
        user_data_dict = dict(request.form)
    # 3. Cuối cùng thử lấy từ URL parameters (?move=...)
    elif request.args:
        user_data_dict = dict(request.args)
    
    # Chuyển đổi thành chuỗi JSON để gửi qua Socket
    user_data_str = json.dumps(user_data_dict)
    
    print(f"Flask nhận được: {user_data_str}") # Log để debug

    # Gửi dữ liệu tới server UDP và nhận phản hồi
    response = send_to_udp_server(user_data_str)
    return response

# Khởi chạy ứng dụng
if __name__ == '__main__':
    # threaded=True là quan trọng để Flask xử lý nhiều người chơi cùng lúc
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
# import packages
import socket
import json
import threading # 1. Import thư viện threading

# define IP and PORT
IP = '0.0.0.0'
PORT = 8888
BYTES = 1024

# create server side socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((IP, PORT))

# Tạo Lock để đồng bộ hóa dữ liệu khi nhiều luồng cùng truy cập 'boards'
board_lock = threading.Lock() 

# initialize game boards
boards = []
for index in range(5):
    boards.append({
        'id': index + 1,
        'red': False,      # player "red" not connected
        'black': False,    # player "black" not connected
        'moves': []
    })

# Helper functions
def reset_board(game_id):
    boards[game_id] = {
        'id': game_id + 1,
        'red': False,
        'black': False,
        'moves': []
    }

def handle_connect(game, side):
    if side in ['red', 'black'] and not game[side]:
        game[side] = True
        return f"{side} connected"
    return f"{side} already connected or invalid"

def handle_disconnect(game, game_id):
    reset_board(game_id)
    return "Disconnected and board reset"

def handle_move(game, move):
    try:
        move = int(move)  # Ensure move is an integer
        game['moves'].append(move)
        return "Move registered"
    except ValueError:
        return "Invalid move format"

# 2. Hàm xử lý logic cho từng Client (chạy trên thread riêng)
def process_client_request(client_data_bytes, client_addr):
    # Parse client data
    try:
        client_data = json.loads(client_data_bytes.decode())
        print(f'[Thread-{threading.get_ident()}] Received from {client_addr}: {client_data}')
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data from client.")
        server_socket.sendto(b'Invalid data format', client_addr)
        return

    # --- BẮT ĐẦU CRITICAL SECTION (Khóa dữ liệu dùng chung) ---
    with board_lock: 
        # Process the game board based on gameId
        try:
            game_id = int(client_data.get('gameId')) - 1
            if game_id < 0 or game_id >= len(boards):
                raise IndexError("Invalid game ID")
            game = boards[game_id]
        except (ValueError, IndexError) as e:
            print(e)
            server_socket.sendto(b'Board does not exist', client_addr)
            return # Thoát hàm nếu lỗi

        # Handle the move request
        action = client_data.get('move')
        side = client_data.get('side', '')  # Either "red" or "black"
        
        if action == 'connect':
            response = handle_connect(game, side)
        elif action == 'disconnect':
            response = handle_disconnect(game, game_id)
        elif action == 'get':
            response = json.dumps(game)
        else:
            response = handle_move(game, action)
    # --- KẾT THÚC CRITICAL SECTION (Tự động mở khóa) ---

    # Send response back to client
    server_socket.sendto(str.encode(response), client_addr)
    print(f'[Thread-{threading.get_ident()}] Sent response to {client_addr}: {response}')


# Listen for incoming requests
print(f"Server is listening on {IP}:{PORT}...")
try:
    while True:
        # Main thread chỉ nhận dữ liệu, không xử lý logic
        client_data, client_addr = server_socket.recvfrom(BYTES)
        
        # 3. Tạo luồng mới để xử lý yêu cầu này
        t = threading.Thread(target=process_client_request, args=(client_data, client_addr))
        t.start() # Khởi chạy luồng

finally:
    # Close server socket on exit
    server_socket.close()
    print("Server socket closed.")
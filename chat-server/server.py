import socket
import threading
from protocol import recv_message, send_message

HOST = '127.0.0.1'
PORT = 8000

clients = {}

clients_lock = threading.Lock()


def broadcast(message_text: str, sender_socket=None):
    with clients_lock:
        for client_socket in list(clients.keys()):
            if client_socket != sender_socket:
                try:
                    send_message(client_socket, "TEXT", message_text.encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError):
                    pass


def handle_client(client_socket, address):
    username = None

    try:
        while True:
            msg = recv_message(client_socket)

            if msg is None:
                break

            command, payload = msg

            if command == "JOIN":
                username = payload.decode('utf-8')
                with clients_lock:
                    clients[client_socket] = username
                print(f"{address} Зарегистрировался как {username}")
                broadcast(f"Пользователь {username} присоединился к чату.")

            elif command == "TEXT":
                if username:
                    text_msg = payload.decode('utf-8')
                    broadcast(f"{username}: {text_msg}", sender_socket=client_socket)
                else:
                    send_message(client_socket, "ERROR", b"You must JOIN first!")

            elif command == "LIST":
                with clients_lock:
                    user_list = ", ".join(clients.values())
                send_message(client_socket, "TEXT", f"Активные пользователи: {user_list}".encode('utf-8'))

            elif command == "QUIT":
                break

            else:
                send_message(client_socket, "ERROR", b"Unknown command")

    except ConnectionResetError:
        print(f"{address} ConnectionResetError: Клиент аварийно разорвал соединение.")
    except BrokenPipeError:
        print(f"{address} BrokenPipeError: Соединение потеряно при отправке.")
    except Exception as e:
        print(f"{address} Произошла непредвиденная ошибка: {e}")

    finally:
        with clients_lock:
            if client_socket in clients:
                disconnected_user = clients.pop(client_socket)


        if 'disconnected_user' in locals():
            broadcast(f"Пользователь {disconnected_user} покинул чат.")
            print(f"Пользователь {disconnected_user} отключен.")

        client_socket.close()


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Чат-сервер запущен на {HOST}:{PORT}")

    try:
        while True:
            client_sock, addr = server_socket.accept()
            print(f"Новое подключение: {addr}")

            client_thread = threading.Thread(
                target=handle_client,
                args=(client_sock, addr),
                daemon=True
            )
            client_thread.start()

    except KeyboardInterrupt:
        print("\nОстановка сервера...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
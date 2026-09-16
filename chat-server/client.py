import socket
import threading
import sys
from protocol import send_message, recv_message

HOST = '127.0.0.1'
PORT = 8000


def receive_messages(sock):
    try:
        while True:
            msg = recv_message(sock)

            if msg is None:
                print("\nСервер закрыл соединение. Нажмите Enter для выхода")
                break

            command, payload = msg

            if command == "TEXT":
                print(f"\n{payload.decode('utf-8')}")
            elif command == "ERROR":
                print(f"\nОШИБКА: {payload.decode('utf-8')}")
            else:
                print(f"\nНЕИЗВЕСТНЫЙ ОТВЕТ: {command} {payload}")

    except ConnectionResetError:
        print("\nConnectionResetError: Сервер неожиданно упал или разорвал соединение. Нажмите Enter для выхода")
    except Exception as e:
        print(f"\nОшибка чтения: {e}")


def main():
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_sock.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Не удалось подключиться к серверу.")
        return

    username = input("Введите ваше имя для входа в чат: ").strip()
    if not username:
        username = "Anonym"

    try:
        send_message(client_sock, "JOIN", username.encode('utf-8'))

        recv_thread = threading.Thread(target=receive_messages, args=(client_sock,), daemon=True)
        recv_thread.start()

        print(f"Вы подключены! Доступные команды: /list (список), /quit (выход)")

        while True:
            user_input = input()

            if user_input.strip() == "/quit":
                send_message(client_sock, "QUIT", b"")
                break
            elif user_input.strip() == "/list":
                send_message(client_sock, "LIST", b"")
            elif user_input:
                try:
                    send_message(client_sock, "TEXT", user_input.encode('utf-8'))
                except BrokenPipeError:
                    print("\nBrokenPipeError: Соединение разорвано, невозможно отправить сообщение")
                    break

    except ConnectionResetError:
        print("\nConnectionResetError: Соединение с сервером потеряно")
    except KeyboardInterrupt:
        print("\nВыход из чата по Ctrl+C...")
    finally:
        print("Закрытие соединения...")
        client_sock.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
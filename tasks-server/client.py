import socket
import threading
import protocol as proto

HOST = "127.0.0.1"
PORT = 5555


def listen_loop(sock, stop_event):
    while not stop_event.is_set():
        try:
            msg = proto.recv_message(sock)
        except (ConnectionResetError, OSError):
            msg = None
        if msg is None:
            print("\n[!] соединение с сервером потеряно")
            stop_event.set()
            break
        command, payload = msg
        text = payload
        if command == "LIST":
            print(f"\n[Список задач]\n{text}\n> ", end="")
        elif command == "ERRO":
            print(f"\n[Ошибка] {text}\n> ", end="")
        else:
            print(f"\n{text}\n> ", end="")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except (ConnectionRefusedError, OSError) as e:
        print(f"Не удалось подключиться: {e}")
        return

    stop_event = threading.Event()
    threading.Thread(target=listen_loop, args=(sock, stop_event), daemon=True).start()

    print("Команды: /add <text>, /list, /done <number>, /quit, /delete <номер>.")
    try:
        while not stop_event.is_set():
            line = input("> ")
            if line.startswith("/add"):
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    print("[!] Ошибка: введите текст задачи.")
                    continue
                proto.send_message(sock, "ADD", parts[1].encode())
            elif line == "/list":
                proto.send_message(sock, "LIST", b"")
            elif line.startswith("/done"):
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    print("[!] Ошибка: укажите номер задачи.")
                    continue
                proto.send_message(sock, "DONE", parts[1].encode())
            elif line.startswith("/delete"):
                parts = line.split(maxsplit=1)
                if len(parts) < 2:
                    print("[!] Ошибка: укажите номер задачи.")
                    continue
                proto.send_message(sock, "DELT", parts[1].encode())
            elif line == "/quit":
                proto.send_message(sock, "QUIT")
                break
            elif line:
                print(f"\n[!] несуществующая команда.\nКоманды: /add <text>, /list, /done <number>, /quit, /delete <номер>.")
                continue
    except (EOFError, KeyboardInterrupt, BrokenPipeError, OSError):
        pass
    finally:
        stop_event.set()
        sock.close()


if __name__ == "__main__":
    main()
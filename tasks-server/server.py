import socket
import threading
import protocol as proto

HOST = "0.0.0.0"
PORT = 5555

tasks = {1 : ("Купить кофе", 0)}
tasks_lock = threading.Lock()


def handle_client(sock, addr):
    print(f"[+] {addr} присоединился")
    try:
        while True:
            msg = proto.recv_message(sock)
            if msg is None:
                break

            command, payload = msg
            if command == "ADD":
                with tasks_lock:
                    new_id = max(tasks.keys(), default=0) + 1
                    tasks[new_id] = (payload, 0)
                proto.send_message(sock, "TEXT", "[*] задача успешно добавлена".encode())
                print(f"[+] {addr} добавил задачу {new_id}. {payload}")
            elif command == "LIST":
                tasks_list = []
                with tasks_lock:
                    for task_number, task in tasks.items():
                        task_name, task_status = task
                        if task_status == 1:
                            tasks_list.append(f"{task_number}. [✓] {task_name}")
                        else:
                            tasks_list.append(f"{task_number}. [x] {task_name}")
                proto.send_message(sock, "LIST", "\n".join(tasks_list).encode())
            elif command == "QUIT":
                print(f"[-] {addr} вышел через QUIT")
                try:
                    proto.send_message(sock, "TEXT", b"* bye")
                except (ConnectionResetError, BrokenPipeError, OSError):
                    pass

                break
            elif command == "DONE":
                try:
                    task_id = int(payload)
                except ValueError:
                    proto.send_message(sock, "ERRO", "номер задачи должен быть числом".encode())
                    continue

                with tasks_lock:
                    if task_id in tasks:
                        task_name, _ = tasks[task_id]
                        tasks[task_id] = (task_name, 1)
                        proto.send_message(sock, "TEXT", "[*] состояние задачи успешно изменено".encode())
                        print(f"[*] {addr} изменил состояние задачи {task_id}")
                    else:
                        proto.send_message(sock, "ERRO", f"задача {task_id} не найдена".encode())
            elif command == "DELT":
                try:
                    task_id = int(payload)
                except ValueError:
                    proto.send_message(sock, "ERRO", "номер задачи должен быть числом".encode())
                    continue

                with tasks_lock:
                    if task_id in tasks:
                        task_name, _ = tasks[task_id]
                        tasks.pop(task_id, None)
                        proto.send_message(sock, "TEXT", f"[*] задача {int(payload)}. {task_name} успешно удалена".encode())
                        print(f"[-] {addr} удалил задачу {int(payload)}. {task_name}")
                    else:
                        proto.send_message(sock, "ERRO", f"задача {task_id} не найдена".encode())
            else:
                proto.send_message(sock, "ERRO", f"unknown command {command}".encode())

    except ConnectionResetError:
        print(f"[!] {addr} - соединение сброшено (RST)")
    except BrokenPipeError:
        print(f"[!] {addr} - не удалось отправить, соединение разорвано")
    finally:
        sock.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"[*] сервер слушает {HOST}:{PORT}")
        while True:
            client_sock, addr = server.accept()
            threading.Thread(target=handle_client, args=(client_sock, addr), daemon=True).start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] сервер остановлен")
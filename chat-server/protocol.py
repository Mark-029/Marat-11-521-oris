import struct

MAX_MESSAGE_SIZE = 10 * 1024 * 1024

def recv_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            raise ConnectionError("Соединение закрыто до получения всех данных")
        data.extend(packet)
    return bytes(data)


def send_message(sock, command: str, payload: bytes):
    command_bytes = command.ljust(4).encode('utf-8')[:4]
    length_bytes = struct.pack("!I", len(payload))

    message = command_bytes + length_bytes + payload

    sock.sendall(message)


def recv_message(sock):
    try:
        header = recv_exact(sock, 8)
        command_bytes = header[:4]
        length_bytes = header[4:]

        command = command_bytes.decode('utf-8').strip()
        payload_length = struct.unpack("!I", length_bytes)[0]

        if payload_length > MAX_MESSAGE_SIZE:
            raise ValueError(f"Сообщение слишком большое: {payload_length} байт")

        payload = recv_exact(sock, payload_length)

        return command, payload

    except ConnectionError:
        return None
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")
        return None
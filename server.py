import socket
from datetime import datetime
from os.path import join as join_path, isfile
from threading import Thread

from settings import *


def add_log(date, addr, path):
    with open(LOGS, "a") as logs:
        logs.write(f"<{date}> {addr}: {path}\n")


def generate_path(request):
    path = request.split("\n")[0].split(" ")[1][1:]
    if not path:
        path = DEFAULT_PATH
    return join_path(DIRECTORY, path)


def get_extension(path):
    return path.split(".")[-1]


def get_code(path, extension):
    if not isfile(path):
        return 404
    elif extension not in ALLOWED_TYPES:
        return 403
    else:
        return 200


def read_file(path):
    return open(path, "rb").read()


def get_date():
    return datetime.now().strftime('%a, %d %b %Y %H:%M:%S GTM')


def process(request, addr):
    path = generate_path(request)
    extension = get_extension(path)
    code = get_code(path, extension)
    date = get_date()
    body = b""
    if code == 200:
        body = read_file(path)
    else:
        extension = "html"
    response = RESPONSE_PATTERN.format(code, CODES[code], date, TYPES[extension], len(body)).encode() + body
    add_log(date, addr, path)
    return response


def handle(conn: socket.socket, addr):
    with conn:
        request = conn.recv(BUFFER_SIZE).decode()
        print(request)
        if request:
            print(request)
            response = process(request, addr)
            conn.send(response)


def accept(sock):
    while True:
        conn, (addr, port) = sock.accept()
        print(f"Connected {addr, port}")
        Thread(target=handle, args=[conn, addr]).start()


def main():
    sock = socket.socket()
    try:
        sock.bind((HOST, PORT))
        print((HOST, PORT))
    except OSError:
        sock.bind((HOST, RESERVE_PORT))
        print((HOST, RESERVE_PORT))
    sock.listen(10)
    accept(sock)


if __name__ == '__main__':
    main()

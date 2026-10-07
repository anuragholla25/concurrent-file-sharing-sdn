import socket
import os
import threading

SERVER_HOST = "10.0.0.4"
SERVER_PORT = 5000


def send_command(sock, command):
    sock.sendall((command + "\n").encode())
    response = sock.recv(4096)
    return response.decode().strip()


def upload_file(sock, filepath):
    if not os.path.isfile(filepath):
        print("File does not exist.")
        return

    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    sock.sendall(
        f"UPLOAD {filename} {filesize}\n".encode()
    )

    response = sock.recv(1024).decode().strip()

    if response != "READY":
        print("Server:", response)
        return

    with open(filepath, "rb") as file:
        while True:
            data = file.read(4096)

            if not data:
                break

            sock.sendall(data)

    response = sock.recv(1024).decode().strip()
    print("Server:", response)


def download_file(sock, filename):

    sock.sendall(
        f"DOWNLOAD {filename}\n".encode()
    )

    response = sock.recv(4096).decode().strip()

    if not response.startswith("FILE_SIZE"):
        print("Server:", response)
        return

    filesize = int(response.split()[1])

    print(f"Server: FILE_SIZE {filesize}")

    sock.sendall(b"READY\n")

    os.makedirs("client/downloads", exist_ok=True)

    output_path = os.path.join(
        "client/downloads",
        filename
    )

    received = 0

    with open(output_path, "wb") as file:

        while received < filesize:

            data = sock.recv(
                min(4096, filesize - received)
            )

            if not data:
                break

            file.write(data)
            received += len(data)

    if received == filesize:

        print(
            f"Download successful: {output_path}"
        )

    else:

        print(
            f"Download failed: "
            f"received {received}/{filesize} bytes"
        )


def main():

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    print(f"Connecting to {SERVER_HOST}:{SERVER_PORT}...")

    sock.connect(
        (SERVER_HOST, SERVER_PORT)
    )

    welcome = sock.recv(1024)
    print(welcome.decode().strip())

    while True:

        command = input("Command: ").strip()

        if command.startswith("UPLOAD "):

            filepath = command.split(" ", 1)[1]

            upload_file(
                sock,
                filepath
            )

        elif command.startswith("DOWNLOAD "):

            filename = command.split(" ", 1)[1]

            download_file(
                sock,
                filename
            )

        else:

            response = send_command(
                sock,
                command
            )

            print("Server:", response)

            if command.upper() == "QUIT":
                break



if __name__ == "__main__":
    main()


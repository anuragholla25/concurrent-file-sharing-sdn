import socket
import os
import threading

HOST = "0.0.0.0"
PORT = 5000

FILES_DIR = "server/files"

USERS = {
    "alice": "1234",
    "bob": "5678"
}

os.makedirs(FILES_DIR, exist_ok=True)


def receive_file(client_socket, filename, filesize):
    filepath = os.path.join(FILES_DIR, filename)

    received = 0

    with open(filepath, "wb") as file:
        while received < filesize:
            data = client_socket.recv(
                min(4096, filesize - received)
            )

            if not data:
                break

            file.write(data)
            received += len(data)

    return received


def handle_client(client_socket, client_address):

    print(f"[+] Client connected: {client_address}")

    authenticated = False

    try:
        client_socket.sendall(
            b"Welcome to Concurrent File Sharing Server!\n"
        )

        while True:

            data = client_socket.recv(1024)

            if not data:
                break

            command = data.decode().strip()

            print(f"[{client_address}] Command: {command}")

            # LOGIN
            if command.startswith("LOGIN"):

                parts = command.split()

                if len(parts) != 3:
                    client_socket.sendall(
                        b"ERROR Invalid LOGIN format\n"
                    )
                    continue

                username = parts[1]
                password = parts[2]

                if username in USERS and USERS[username] == password:
                    authenticated = True

                    client_socket.sendall(
                        b"LOGIN_SUCCESS\n"
                    )

                    print(f"[+] {username} authenticated")

                else:
                    client_socket.sendall(
                        b"LOGIN_FAILED\n"
                    )

            # LIST
            elif command == "LIST":

                if not authenticated:
                    client_socket.sendall(
                        b"ERROR Please login first\n"
                    )
                    continue

                files = os.listdir(FILES_DIR)

                if not files:
                    client_socket.sendall(
                        b"FILE_LIST_EMPTY\n"
                    )
                else:
                    response = "\n".join(files)
                    client_socket.sendall(
                        (response + "\n").encode()
                    )

            # UPLOAD filename filesize
            elif command.startswith("UPLOAD"):

                if not authenticated:
                    client_socket.sendall(
                        b"ERROR Please login first\n"
                    )
                    continue

                parts = command.split()

                if len(parts) != 3:
                    client_socket.sendall(
                        b"ERROR Invalid UPLOAD format\n"
                    )
                    continue

                filename = os.path.basename(parts[1])

                try:
                    filesize = int(parts[2])
                except ValueError:
                    client_socket.sendall(
                        b"ERROR Invalid file size\n"
                    )
                    continue

                client_socket.sendall(
                    b"READY\n"
                )

                received = receive_file(
                    client_socket,
                    filename,
                    filesize
                )

                if received == filesize:
                    client_socket.sendall(
                        b"UPLOAD_SUCCESS\n"
                    )

                    print(
                        f"[+] Uploaded {filename} "
                        f"({filesize} bytes)"
                    )
                else:
                    client_socket.sendall(
                        b"UPLOAD_FAILED\n"
                    )

                        # DOWNLOAD filename
            elif command.startswith("DOWNLOAD"):

                if not authenticated:
                    client_socket.sendall(
                        b"ERROR Please login first\n"
                    )
                    continue

                parts = command.split()

                if len(parts) != 2:
                    client_socket.sendall(
                        b"ERROR Invalid DOWNLOAD format\n"
                    )
                    continue

                filename = os.path.basename(parts[1])
                filepath = os.path.join(FILES_DIR, filename)

                if not os.path.isfile(filepath):
                    client_socket.sendall(
                        b"ERROR File not found\n"
                    )
                    continue

                filesize = os.path.getsize(filepath)

                client_socket.sendall(
                    f"FILE_SIZE {filesize}\n".encode()
                )

                response = client_socket.recv(1024)

                if response.decode().strip() != "READY":
                    continue

                with open(filepath, "rb") as file:

                    while True:

                        data = file.read(4096)

                        if not data:
                            break

                        client_socket.sendall(data)

                print(
                    f"[+] Downloaded {filename} "
                    f"({filesize} bytes)"
                )
            # QUIT
            elif command == "QUIT":

                client_socket.sendall(
                    b"GOODBYE\n"
                )

                break

            else:

                client_socket.sendall(
                    b"ERROR Unknown command\n"
                )

    except Exception as e:
        print(f"[!] Error: {e}")

    finally:
        client_socket.close()

        print(
            f"[-] Client disconnected: {client_address}"
        )


server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind(
    (HOST, PORT)
)

server_socket.listen(5)

print("=" * 40)
print("Concurrent File Sharing Server")
print(f"Listening on {HOST}:{PORT}")
print("=" * 40)

while True:
    client_socket, client_address = server_socket.accept()

    client_thread = threading.Thread(
        target=handle_client,
        args=(client_socket, client_address)
    )
    client_thread.start()


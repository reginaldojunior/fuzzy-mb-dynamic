import socket

def main():
    ip = "127.0.0.1"  # IP do servidor
    port = 9030  # Porta do servidor

    socketChannel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketChannel.connect((ip, port))

    while True:
        data = socketChannel.recv(1024).decode("utf-8")
        if not data:
            break
        lines = data.split("#")
        for line in lines:
            if line == "$$":
                break
            print(line)

    socketChannel.close()

if __name__ == "__main__":
    main()

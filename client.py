import socket
import threading

def listen_server(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if msg:
                print(msg, end="")
        except:
            break

def main():
    host = '127.0.0.1'
    port = 65432

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

    while True:
        prompt = sock.recv(1024).decode()
        print(prompt, end="")
        name = input()
        sock.sendall(name.encode())

        response = sock.recv(1024).decode()
        print(response, end="")
        if "Bun venit" in response:
            break

    threading.Thread(target=listen_server, args=(sock,), daemon=True).start()

    while True:
        guess = input()
        if len(guess) == 4 and guess.isdigit():
            sock.sendall(guess.encode())
        else:
            print("Trimite un numar valid de 4 cifre.")

if __name__ == "__main__":
    main()
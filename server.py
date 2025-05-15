import socket
import threading
import random

clients = {}
attempts = {}
secret_number = ""


def generate_number():
    digits = list("0123456789")
    random.shuffle(digits)
    return ''.join(digits[:4])


def evaluate_guess(secret, guess):
    centered = sum(secret[i] == guess[i] for i in range(4))
    uncentered = sum(min(secret.count(d), guess.count(d)) for d in guess) - centered
    return centered, uncentered


def broadcast(message):
    for client in clients.values():
        try:
            client.sendall(f"[SERVER] {message}\n".encode())
        except:
            pass


def handle_client(conn, addr):
    global secret_number
    name = ""

    try:
        while True:
            conn.sendall("Introdu un nume unic: ".encode())
            name = conn.recv(1024).decode().strip()
            if not name:
                conn.close()
                return
            if name in clients:
                conn.sendall("Nume deja folosit. Incearca altul.\n".encode())
            else:
                break

        clients[name] = conn
        attempts[name] = 0
        conn.sendall(f"Bun venit, {name}! Jocul a inceput. Ghiceste un numar de 4 cifre diferite.\n".encode())

        while True:
            data = conn.recv(1024).decode().strip()
            if not data:
                break

            if len(data) != 4 or not data.isdigit() or len(set(data)) != 4:
                conn.sendall("Numar invalid! Trimite un numar de 4 cifre diferite.\n".encode())
                continue

            attempts[name] += 1
            centered, uncentered = evaluate_guess(secret_number, data)
            conn.sendall(f"{centered} centrate, {uncentered} necentrate\n".encode())

            if centered == 4:
                broadcast(f"{name} a ghicit numarul {secret_number} in {attempts[name]} incercari!")
                secret_number = generate_number()
                print(f"[SERVER] Numar nou generat: {secret_number}")
                for player in clients:
                    attempts[player] = 0
                broadcast("Joc nou! Se genereaza un nou numar. Puteti incepe sa ghiciti din nou!")

    except:
        pass
    finally:
        conn.close()
        if name in clients:
            del clients[name]
        if name in attempts:
            del attempts[name]


def main():
    global secret_number
    host = '127.0.0.1'
    port = 65432

    secret_number = generate_number()
    print(f"[SERVER] Numar secret generat: {secret_number}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()

    print(f"[SERVER] Serverul asculta la {host}:{port}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
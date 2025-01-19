import socket
import pandas as pd

def get_list(message):
    # Process string
    message = message.replace("[", "")
    message = message.replace("]", "")
    message = message.replace(" ", "")
    values = message.split(',')

    # Build int list from values
    values = [int(x) for x in values if x.isdigit()]

    return values


if __name__ == "__main__":
    client_list = get_list(input("Input list:\n"))

    request = ""
    while request != "max" and request != "mean":
        request = input("Choose option:\n")

    servers = pd.read_csv("servers.csv")

    host, port = servers.loc[0, 'ip'], servers.loc[0, 'port']

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    client_socket.send(f"{request} {str(client_list)}".encode('utf-8'))

    response = client_socket.recv(1024).decode('utf-8')

    print(f"{client_list} -> {request} = {response}")
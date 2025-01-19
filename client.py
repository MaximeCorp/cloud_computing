import socket
import threading
from random import randint
import pandas as pd


receiving_list = []

def client_program(server: tuple, sublist: list[int], option: str) -> None:
    host = server[0]
    port = server[1]
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print("Connected to server.")
    except Exception as e:
        print(f"Connection error: {e}")

    client_socket.send(f"{option} {str(sublist)}".encode('utf-8'))
    response = client_socket.recv(1024).decode('utf-8')
    answer = float(response)
    print(f"Received from server: {answer}")
    receiving_list.append(answer)
    client_socket.close()
    print("Connection closed.")


# Run the client program
if __name__ == "__main__":
    # Read the servers from the csv file
    servers = pd.read_csv('servers.csv')
    # list of tuples (server, port)
    servers = [(server, port) for server, port in zip(servers['ip'], servers['port'])]
    random_numbers = [randint(0, 100) for _ in range(len(servers) * 10)]
    print(random_numbers)
    # divide the list into len(servers) sublists
    sublist = [random_numbers[i:i + len(random_numbers) // len(servers)] for i in range(0, len(random_numbers), len(random_numbers) // len(servers))]
    print("1. for mean of the list")
    print("2. for max of the list")
    choice = input("Enter your choice: ")
    while choice not in ['1', '2']:
        choice = input("Enter your choice: ")
    option = "mean"
    if choice == '2':
        option = "max"
    for idx, server in enumerate(servers):
        threading.Thread(target=client_program, args=(server, sublist[idx], option,)).start()
    # wait for all threads to finish
    while threading.active_count() > 1:
        pass
    print(f"{option} list: {receiving_list}")

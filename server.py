import socket
import time

import pandas as pd
import threading


def get_own_ip():
    # Create a temporary socket
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a remote server
        temp_socket.connect(('10.255.255.255', 1))
        # Get the socket's own address
        own_ip = temp_socket.getsockname()[0]
    except Exception as e:
        print("Failed to get own IP address:", e)
        own_ip = None
    finally:
        # Close the temporary socket
        temp_socket.close()
    return own_ip


def get_list(message):
    # Process string
    message = message.replace("[", "")
    message = message.replace("]", "")
    message = message.replace(" ", "")
    values = message.split(',')

    # Build int list from values
    values = [int(x) for x in values if x.isdigit()]

    return values


class Task:
    def __init__(self, socket, option, task, date):
        self.socket = socket
        self.option = option
        self.task = task
        self.date = date

    def timestamp(self):
        return time.time() - self.date


class Server:
    def __init__(self):
        # Server's informations
        self.host = '0.0.0.0'
        self.ip = None
        while self.ip is None:
            self.ip = get_own_ip()

        # Hardcoded servers
        servers = pd.read_csv('servers.csv')

        # Waiting queue
        self.incoming = []

        # Receive on corresponding ports
        for i, row in servers.iterrows():
            if self.ip == row['ip']:
                thread = threading.Thread(target=self.get_connections, args=(row['port'],))
                thread.start()

        # Ready queue
        self.ready = []

        # Start long term scheduling
        long_thread = threading.Thread(target=self.long_term_management)
        long_thread.start()

        # Start short term scheduling
        short_thread = threading.Thread(target=self.short_term_management)
        short_thread.start()

    def get_connections(self, port):
        # Server socket creation
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set up to accept connections
        server_socket.bind((self.ip, port))
        server_socket.listen(10)

        # Accept and process clients
        while True:
            client_socket, client_address = server_socket.accept()
            thread = threading.Thread(target=self.receive_tasks, args=(client_socket,))
            thread.start()

    def receive_tasks(self, client_socket):
        while True:
            # Receive list string
            message = client_socket.recv(1024).decode('utf-8')

            if not message:
                break

            i = message.find('[')

            option = message[:i-1]
            task = get_list(message[i:])

            date = time.time()

            # Add task to waiting queue
            self.incoming.append(Task(client_socket, option, task, date))
            print(f"{task} moved to waiting queue")

    def long_term_management(self):
        while True:
            # Check if any task in waiting queue
            n = len(self.incoming)
            if n > 0:
                # Find next task
                i = 0
                minimum = 0
                score = len(self.incoming[0].task) / max(self.incoming[0].timestamp(), 0.0001)

                for task in self.incoming:
                    temp = len(task.task) / max(self.incoming[0].timestamp(), 0.0001)
                    if temp < score:
                        minimum = i
                        score = temp
                    i += 1

                # Remove from waiting queue
                chosen = self.incoming.pop(minimum)

                # Add to ready queue
                self.ready.append(chosen)
                print(f"{chosen.task} moved to ready queue")

                # Artificial delay to make it humanly understandable
                time.sleep(len(chosen.task) * 0.2)

    def short_term_management(self):
        while True:
            # FIFO short term management
            if len(self.ready) > 0:
                task = self.ready.pop(0)
                if task.option == "max":
                    self.long_max_finding(task)
                elif task.option == "mean":
                    self.long_mean_finding(task)

    def long_max_finding(self, task):
        # Find maximum
        values = task.task
        maximum = values[0]
        print(f"[{maximum}", end="")

        for value in values[1:]:
            # Artificial delay
            time.sleep(0.125)
            print(f", {value}", end="")
            if value > maximum:
                maximum = value
        print(f"] max: {maximum}")

        # Send result to client
        task.socket.send(str(maximum).encode('utf-8'))

    def long_mean_finding(self,task):
        # Find maximum
        values = task.task
        mean = values[0]
        print(f"[{mean}", end="")

        for value in values[1:]:
            # Artificial delay
            time.sleep(0.125)
            print(f", {value}", end="")
            mean += value

        mean /= len(values)
        print(f"] mean: {mean}")

        # Send result to client
        task.socket.send(str(mean).encode('utf-8'))


if __name__ == "__main__":
    server = Server()
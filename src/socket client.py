import socket

def handle_input_request(prompt):
    response = input(prompt)
    return response

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 9999))

    role_name = input("Enter your role: ")
    employee_id = input("Enter your employee ID: ")

    # Send initial request to display menu
    initial_request = f"{role_name},{employee_id}"
    client.send(initial_request.encode('utf-8'))
    response = client.recv(4096).decode('utf-8')
    print(f"Received response:\n{response}")

    while True:
        command = input("Enter your command (or type 'exit' to quit): ")
        if command.lower() == 'exit':
            break

        args = []
        if role_name == 'Admin' and command in ['1', '2', '3']:
            if command == '1':
                args.append(handle_input_request("Enter food name: "))
                args.append(handle_input_request("Enter food price: "))
            elif command == '2':
                args.append(handle_input_request("Enter food id: "))
                args.append(handle_input_request("Enter food name: "))
                args.append(handle_input_request("Enter food price: "))
            elif command == '3':
                args.append(handle_input_request("Enter food id: "))
        elif role_name == 'Employee' and command in ['2', '3']:
            if command == '2':
                args.append(handle_input_request("Enter food item ID to select: "))
            elif command == '3':
                args.append(handle_input_request("Enter food item ID: "))
                args.append(handle_input_request("Enter your comment: "))
                args.append(handle_input_request("Enter your rating (1-5): "))
        elif role_name == 'Chef' and command == '1':
            args.append(handle_input_request("Enter the meal type (e.g., breakfast, lunch, dinner): "))

        request = f"{role_name},{employee_id},{command},{','.join(args)}"
        client.send(request.encode('utf-8'))
        response = client.recv(4096).decode('utf-8')
        print(f"Received response:\n{response}")

    client.close()

if __name__ == "__main__":
    main()

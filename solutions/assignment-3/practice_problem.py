import socket
import argparse
import struct
import time

def server(interface, port):
    '''
    Server listens at default port 50000 in the local system for incoming connections.
    It expects a bytestream data, decodes and expects two space separated integers.
    Calculates the sum and sends it back.
    '''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((interface, port))
    sock.listen(1)
    print('Listening for connections at', sock.getsockname())
    while True:
        print('Waiting to accept a new connection...')
        conn_obj, client_addr = sock.accept()
        print('Accepted connection from', client_addr)
        package_recv = recv_msg(conn_obj)
        print('Numbers received:', package_recv.decode())
        calc_sum = sum(map(int, package_recv.split()))
        time.sleep(2)
        send_msg(conn_obj, str(calc_sum))
        conn_obj.close()
        print('Reply sent, connection closed.')

def client(host, port):
    '''
    Client sends two numbers given by the user as byte stream to the localhost at default port 50000.
    '''

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print('Client has been assigned socket:', sock.getsockname())
    numbers = input("Enter two numbers separated by a space: ")
    sock.connect((host, port))
    send_msg(sock, numbers)
    reply = recv_msg(sock)
    calc_sum = sum(map(int, numbers.split()))
    if int(reply) == calc_sum:
        print('Reply correct!')
    else:
        print('Reply incorrect! Got %s instead of %d.' % (reply, str(calc_sum)))
    sock.close()

def send_msg(sock, msg):
    msg = struct.pack('I', len(msg)) + msg.encode()
    sock.sendall(msg)

def recv_msg(sock):
    raw_msglen = recvall(sock, 4) #message length is an integer of size 4
    if not raw_msglen:
        return None
    msglen = struct.unpack('I', raw_msglen)[0]
    return recvall(sock, msglen)

def recvall(sock, msglen):
    data = b''
    while len(data) < msglen:
        packet = sock.recv(msglen - len(data))
        if not packet:
            return None
        data += packet
    return data


if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser()
    parser.add_argument('role', choices=choices)
    parser.add_argument('-host', default="0.0.0.0")
    parser.add_argument('-port', type=int, default=50000)
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.port)

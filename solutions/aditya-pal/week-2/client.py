import socket, sys

client = socket.socket()
host = socket.gethostname()
port = 3333
client.connect((host, port))
n1 = 0
n2 = 0
nms = ""
try:
    nms = str(sys.argv[1]) + " " + str(sys.argv[2])
    n1, n2 = map(int, nms.split())
except:
    print ("Incorrect Input")
    exit(0)
client.send(nms.encode("utf-8"))
data_received = client.recv(1024)
client.close()
data_received = data_received.decode("utf-8")
answer = n1 + n2
try:
    data_received = int(data_received)
    if (data_received == answer):
        print ("Correct!")
    else:
        print("Incorrect!")
except:
    print (data_received)

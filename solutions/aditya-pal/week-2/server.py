import socket, time

svr = socket.socket()
host = socket.gethostname()
port = 3333
svr.bind((host, port))
svr.listen(5)     #max connections = 5
while True:
    try:
        con, add = svr.accept()
        print("Connected by " + str(add))
        nums = con.recv(1024)
        time.sleep(2)
        try:
            n1, n2 = map(int, nums.split())
            sm = n1 + n2
            sm = str(sm)
            con.send(sm.encode("utf-8"))
        except:
            sm = "Incorrect input"
            con.send(sm.encode("utf-8"))
        con.close()
    except EOFError:
        print ("No data")

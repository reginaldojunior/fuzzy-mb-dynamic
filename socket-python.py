import socket
import sys
import time

def main(args):
    if len(args) != 4:
        print("Usage: ServerProducer <ip> <port> <file> <Rate of instances per second>")
        sys.exit(1)
    
    ip = args[0]
    port = int(args[1])
    filename = args[2]
    IPS = int(args[3])
    IPB = IPS // 5
    
    instancesSent = 0
    lines = []
    with open(filename, 'r') as file:
        lines = file.readlines()
    print(f"read {len(lines)} lines to memory from file {filename}.")
    
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.bind((ip, port))
    serverSocket.listen(1)
    print("ServerSocket awaiting connections...", serverSocket.getsockname())
    
    socketChannel, address = serverSocket.accept()
    print("Connection from", address)
    
    if socketChannel:
        socketChannel.setblocking(False)
        
        reading_header = True
        i = 0
        while reading_header:
            l = lines[i]
            if "@data" in l:
                reading_header = False
            i += 1
        
        msg = ""
        keep_going = True
        startTime = 0
        buffer = bytearray(1048576)  # 1048576
        
        limit = len(lines)
        startingAll = time.time()
        lastSuccessfullStep = 0
        while i < limit and keep_going:
            startTime = time.time()
            num_inst = 0
            while num_inst < IPB and i < limit:
                msg = lines[i] + "#"
                buffer = bytes(msg, 'utf-8')
                try:
                    socketChannel.sendall(buffer)
                except socket.error as ex:
                    print("Closed by client!")
                    keep_going = False
                    break
                num_inst += 1
                instancesSent += 1
                i += 1
            
            if not keep_going:
                break
            
            justSent = time.time()
            elapsed = (justSent - startTime) * 1000
            sl = 200 - elapsed if 0 < elapsed < 200 else 0
            time.sleep(sl / 1000)
            
            if (time.time() - startingAll) > 120:
                keep_going = False
        
        totalSpent = time.time() - startingAll
        if keep_going:
            msg = "$$"
            buffer = bytes(msg, 'utf-8')
            try:
                socketChannel.sendall(buffer)
            except socket.error:
                pass
        
        print("\nTotal Time Producer (s):", totalSpent)
        print("Total instances Producer:", instancesSent)
        print("Producer Rate (inst per second):", instancesSent / totalSpent)
        
        socketChannel.close()
    
    serverSocket.close()

if __name__ == "__main__":
    main(sys.argv[1:])

import socket
import sys
import random
import time

### esse metodo serve para calcular o tamanho do mini-batching
### de acordo com a porcentagem de chegada das instancias considerado 10% a 100% [1]
### [1] https://digitalassets.lib.berkeley.edu/techreports/ucb/text/EECS-2014-133.pdf
def calcular_mb(mb_history, ips_history, elapsed_history):
    if (len(mb_history) < 2):
        return int(50)

    xSmall = min(mb_history[-1], mb_history[-2])
    xLarge = max(mb_history[-1], mb_history[-2])

    pSmall = min(elapsed_history[-1], elapsed_history[-2])
    pLarge = max(elapsed_history[-1], elapsed_history[-2]) 

    if (pLarge / xSmall) > (pSmall / xSmall) and elapsed_history[-1] > pLarge:
        mb = (1 - 0.25) * xSmall
    else:
        mb = elapsed_history[-1] / 0.7

    if (mb < 1):
        mb = 50

    print(f'mb -> {mb}')
    return int(mb)

def calcular_mb_simple(ips, limit):
    porcentagem = calcular_porcentagem(ips['ips'], limit)

    if (porcentagem >= 5):
        mb = 2000
    elif (porcentagem >= 3 and porcentagem < 5):
        mb = 1000
    elif (porcentagem >= 2 and porcentagem < 3):
        mb = 500
    elif (porcentagem >= 1 and porcentagem < 2):
        mb = 250
    else:
        mb = 50

    print(f'mb -> {mb}')
    return int(mb)

def calcular_porcentagem(ips, total_instancias):
    porcentagem = (ips / total_instancias) * 100
    return porcentagem

### método responsável por calcular as instancias por byte
### e também do tamanho do mini-batching de acordo com a porcentagem que está chegando na rede
### essa porcentagem é gerada aleatoriamente
def oscilar_instancias_por_segundo(limit):
    limit_per_segundo = limit * 0.05

    ips = random.randint(1, int(limit_per_segundo))
    ipb = ips // 5

    response = { 'ipb': ipb, 'ips': ips }

    return response

### método adaptado de produção de dados em rede através de um socket
def main(args):
    if len(args) != 3:
        print("Usage: ServerProducer <ip> <port> <file>")
        sys.exit(1)
    
    ip = args[0]
    port = int(args[1])
    filename = args[2]

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
        socketChannel.setblocking(True)
        
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
        elapsed = 0

        ips_history = []
        elapsed_history = []
        mb_history = []

        while i < limit and keep_going:
            startTime = time.time()
            num_inst = 0
            
            ips = oscilar_instancias_por_segundo(limit)
            mb = calcular_mb_simple(ips, limit)

            ipb = ips['ipb']

            while num_inst < ipb and i < limit:
                msg = str(mb) + ',' + lines[i] + "#"
                buffer = bytes(msg, 'utf-8')

                try:
                    socketChannel.sendall(buffer)
                except socket.error as ex:
                    print("Closed by client!", ex)
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

            ips_history.append(ips)
            elapsed_history.append(elapsed)
            mb_history.append(mb)

            if (time.time() - startingAll) > 99999999:
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

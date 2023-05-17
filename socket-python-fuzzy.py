import socket
import sys
import random
import time
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

### esse metodo serve para calcular o tamanho do mini-batching
### de acordo com a porcentagem de chegada das instancias considerado 10% a 100%
### de chegada, é utilizado o algoritmo fuzzy do scikit para isso
def calc_minibatching_by_thoughput(thoughput):
    taxa_vazao = ctrl.Antecedent(np.arange(10, 101, 1), 'taxa_vazao')
    minibatching = ctrl.Consequent(np.arange(0, 2050, 50), 'minibatching')

    taxa_vazao.automf(number=5, names=['super_baixo', 'baixo', 'medio', 'alto', 'super_alto'])

    minibatching['super_baixo'] = fuzz.trimf(minibatching.universe, [0, 50, 100])
    minibatching['baixo'] = fuzz.trimf(minibatching.universe, [100, 250, 500])
    minibatching['medio'] = fuzz.trimf(minibatching.universe, [500, 750, 1000])
    minibatching['alto'] = fuzz.trimf(minibatching.universe, [1000, 1250, 1500])
    minibatching['super_alto'] = fuzz.trimf(minibatching.universe, [1500, 1750, 2000])

    regra1 = ctrl.Rule(taxa_vazao['super_baixo'], minibatching['super_baixo'])
    regra2 = ctrl.Rule(taxa_vazao['baixo'], minibatching['baixo'])
    regra3 = ctrl.Rule(taxa_vazao['medio'], minibatching['medio'])
    regra4 = ctrl.Rule(taxa_vazao['alto'], minibatching['alto'])
    regra5 = ctrl.Rule(taxa_vazao['super_alto'], minibatching['super_alto'])

    recomendacao_minibatching = ctrl.ControlSystem([regra1, regra2, regra3, regra4, regra5])
    recomendacao = ctrl.ControlSystemSimulation(recomendacao_minibatching)

    recomendacao.input['taxa_vazao'] = thoughput
    recomendacao.compute()

    return int(round(recomendacao.output['minibatching']))

### método responsável por calcular as instancias por byte
### e também do tamanho do mini-batching de acordo com a porcentagem que está chegando na rede
### essa porcentagem é gerada aleatoriamente
def pega_ipb_e_mb(limit):
    thoughput = dividir_dataset_por_porcentagem_aleatoria(limit)
    ips = thoughput['valor']
    ipb = ips // 5
    print(thoughput)

    mb = calc_minibatching_by_thoughput(int(thoughput['porcentagem'] * 100))
    print({ 'ipb': ipb, 'mb': mb })
    return { 'ipb': ipb, 'mb': mb }

### divide o tamanho total do dataset de acordo com a porcentagem de saida, fazendo
### pedaços de envio, simulando o envio em rede oscilado 
### TODO não está enviando o dataset inteiro, parece que está enviando somente o pedaço gerado aleatoriamente e depois
### a aplicação para de enviar os próximos dados
def dividir_dataset_por_porcentagem_aleatoria(valor):
    porcentagem = random.uniform(0, 0.9)  # Gera um valor aleatório entre 0 e 0.9
    valor = int(valor) * porcentagem
    return { 'valor': valor, 'porcentagem': porcentagem }

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

        ## o mb_control serve para controlar o envio de mensagens de acordo com o tamanho do mb sugerido
        ## pela lógica fuzzy
        mb_control = 0
        while i < limit and keep_going:
            startTime = time.time()
            num_inst = 0
            
            ipb_mb = pega_ipb_e_mb(limit)
            ipb = ipb_mb['ipb']
            mb = ipb_mb['mb']

            # caso o mb_control ultrapasse o tamanho do mb ele é zerado e iniciado um novo laço,
            # desta forma enviando em pedaços o batch
            if mb_control > mb:
                mb_control = 0
                continue
            
            while num_inst < ipb and i < limit:
                # o controle também ocorre quando está enviando as instancias por byte para não correr perigo
                # de enviar informações maior do que o esperado
                if mb_control > mb:
                    mb_control = 0
                    continue

                mb_control += 1
                msg = str(mb) + ',' + lines[i] + "#"
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

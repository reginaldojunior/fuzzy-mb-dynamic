### esse metodo serve para calcular o tamanho do mini-batching
### de acordo com a porcentagem de chegada das instancias considerado 10% a 100%
def calcular_mb(mb_history, ips_history, elapsed_history):
    if (len(mb_history) < 2):
        return int(10)

    if (mb_history[-1] > mb_history[-2]):
        xLarge = mb_history[-1]
        xSmall = mb_history[-2]

        pSmall = elapsed_history[-2]
        pLarge = elapsed_history[-1]
    else:
        xLarge = mb_history[-2]
        xSmall = mb_history[-1]

        pSmall = elapsed_history[-1]
        pLarge = elapsed_history[-2]

    if (pLarge / xSmall) > (pSmall / xSmall) and elapsed_history[-1] > pLarge:
        mb = (1 - 0.25) * xSmall
    else:
        mb = mb_history[-1] / 0.7

    print(f'mb -> {mb}')
    return int(mb)

mb_history = [50, 150]
# ips_history = [300, 600]
# elapsed_history = [5, 8]

# mb = calcular_mb(mb_history, ips_history, elapsed_history)

# mb_history.append(mb)
# ips_history = [300, 600, 30]
# elapsed_history = [5, 8, 15]

# calcular_mb(mb_history, ips_history, elapsed_history)

# mb_history.append(mb)
ips_history = [300, 600, 30, 10]
elapsed_history = [5, 8, 15, 120]

calcular_mb(mb_history, ips_history, elapsed_history)
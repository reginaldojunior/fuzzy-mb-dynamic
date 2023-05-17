import sys
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

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

    return recomendacao.output['minibatching']

thoughput = sys.argv[1]
print(round(calc_minibatching_by_thoughput(int(thoughput))))

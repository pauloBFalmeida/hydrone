# Main (Pt)

## Informações

[Es.py](Es.py) contêm a implementação dos algoritmos OpenAI-ES e CMA-ES

A pasta allCodesOctave contêm os códigos em octave para a execução da função de avaliação

## Como Rodar
Contêm os jupyter-notebooks para execuções e um pouco de análise dos algoritmos, e os arquivos em python para a execução de multiplas vezes do mesmo algoritmo.

Pasta 'run' contêm pastas para cada velocidade da água da forma que o underline substitui o ponto, ou seja a pasta 8_0 é referente V_S = 8.0
Dentro de cada pasta de velocidade tem as pasta com cada uma das 10 execuções do algoritmo.

Cada Execução do algoritmo será criada uma pasta com o horário do começo da execução, e dentro desta pasta outra pasta para cada algoritmo, CMAES ou OpenAIES, e dentro de cada pasta contêm os arquivos csv para cada número de pás da hélice.

## Organização dos algoritmos

Arquivos como [openaies_cmaes_with_constraints](openaies_cmaes_with_constraints.ipynb)

No começo do arquivo tem os imports das libs utilizadas e a definição das ranges das variáveis,

Os algoritmos de otimização utilizam as 3 variáveis, D, AEdAO, PdD.
V_S que é a velocidade da água é fixa.
Z é o número inteiro de pás da hélice, para cada um dos possiveis valores é feita a otimização das outras variáveis, em paralelo.

Depois tem as funções de salvar os resultados em arquivos (csv)
save_file = True, serve para salvar os resultados obtidos em arquivos, se False, então nenhum resultado é salvo (ideal para testes rápidos)
save_in_same_dir = True, salva os resultados do CMA-ES e OPENAI-es dentro da mesma pasta com nome do horário de execução.

Seguido pelas funções de avaliação e fitness
run_octave_evaluation é a função que faz a execução dos códigos do octave
evaluate_solution gera a fitness

test_solver é a função que mantem o loop de iterações (gerações) em que é gerada uma nova populaçao, testados os valores, e salvo o melhor valor encontrado no histórico (history)

solver_for_Z é a função que cuida de chamar a execução do algoritmo para cada Z (wrapper da para chamar a função em paralelo)
get_best_result retorna o melhor resultado da execução do algoritmo para um Z

CMAES parallel é onde é executado a o algoritmo CMA-ES em Z paralelos
depois tem as funções para encontrar o melhor valor valido (dentro das contraints) entre as Z execuções

OPENAI-ES parallel é onde é executado a o algoritmo OPENAI-ES em Z paralelos
depois tem as funções para encontrar o melhor valor valido (dentro das contraints) entre as Z execuções

No final do arquivo é feito um gŕafico com os historicos de cada algortimo, mostrando os valores de fitness para cada geração das Z iterações

E a comparação do melhor resultado entre o CMA-ES e OpenAI-ES

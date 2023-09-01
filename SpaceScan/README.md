# Space Scan (Pt)

## Como usar
Ao rodar o spaceScan ele vai percorrer o espaço das variáveis, com passo determinado pelo dict LIST_SIZE, em que o espaço válido de cada variável é divido por um número inteiro, ou seja se o range da variável D é [0.5, 0.8] e passo de 30, ele vai percorrer o espaço como [0.5, 0.51, 0.52, 0.53 ... 0.78, 0.79, 0.8], para cada elemento da lista de uma variável será feito a execução para todas as outras variáveis. Assim a quantidade de execuções do código de avaliação realizadas serão a multiplicação dos 3 valores em LIST_SIZE, isso para cada número de pás de hélice.

No final da execução todos os resultados são salvos em arquivos csv para cada número de pás de hélice.
Renomear a pasta contendo os CSVs para a velocidade da água (V_S), com o '.' (ponto) trocado por '_' (underline) exemplo V_S= 8.5 para 8_5
Colocar na pasta scans_with_constraints para poder utilizar nos jupyter-notebooks

## Jupyter-Notebooks
[scan_analise_constraints](scan_analise_constraints.ipynb) tem a visualização de uma velocidade, tem os gráficos 3D das constraints e de Brake Power.

[scan_analise_all_with_constraints](scan_analise_all_with_constraints.ipynb) tem a visualização de todas as velocidades, contem o gŕafico em barra com o número de soluções válidas encontradas em cada velocidade.

## Atenção
spaceScan.py precisa usa allCodesOctave do Main, portanto a pasta SpaceScan tem que estar no mesmo diretório do Main (funcionar normal se baixar o projeto inteiro, ou se quiser colocar o allCodesOctave na mesma pasta do .py e mudar a referência usada na função 'run_octave_evaluation')

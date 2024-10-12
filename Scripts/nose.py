#==============
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
import statsmodels.api as sm

class AlphaCalculator:
    def __init__(self, li_fit, ls_fit):
        self.li_fit = li_fit
        self.ls_fit = ls_fit

    def lista0(self, lista1: list, lista2: list) -> tuple:
        filtered = [(l1, l2) for l1, l2 in zip(lista1, lista2) if l1 != 0]
        if filtered:
            lista1, lista2 = zip(*filtered)
            return list(lista1), list(lista2)
        else:
            return [], []
    
    def calculate_alpha(self, data_path):
        G = nx.read_edgelist(data_path, nodetype=int)  # leemos el grafo
        degree_count = nx.degree_histogram(G) 
        degrees = list(range(0, len(degree_count)))

        degree_count, degrees = self.lista0(degree_count, degrees)
        
        # Normalize the degree distribution
        degree_distribution = [count / float(sum(degree_count)) for count in degree_count]
        x0, y0 = np.array(np.log10(degrees)), np.array(np.log10(degree_distribution))
        x, y = x0[(x0 >= self.li_fit) & (x0 <= self.ls_fit)], y0[(x0 >= self.li_fit) & (x0 <= self.ls_fit)]

        x = sm.add_constant(x)
        model = sm.OLS(y, x).fit()
        alpha = -np.round(model.params[1], 2)
        return alpha, x0, y0, model


class GraphAnalyzer():
    
    def __init__ (self, type = ''):
        self._alpha: list = []
        self._values: list = []

        self._type: str = type
        self._id = 0

        self._path: str = ''
        self._edgePath: str = ''
        self._pdfPath: str = ''

        self.alpha_calculator = None



    #TODO: buscarle uso, lo mas probable es que no se utilice
    def clear_value (self):
        self._alpha.clear()
        self._values.clear()

    @property
    def alpha(self):
        return self._alpha
    
    @property
    def values(self):
        return self._values
    
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, type):
        self._type = type
        self.set_path()
        self.create_path()

    def set_path(self):
        self._path = f'../data/transient/{str(self.type)}/'
        self._edgePath = f'{self._path}edgeList'
        self._pdfPath = f'{self._path}pdf'

        print(f'intento: {self._path}')

    def create_path(self):
        l = [self._path, self._edgePath, self._pdfPath]
        for i in l:
            os.makedirs(i, exist_ok=True)

    def lista0 (self, lista1: list, lista2: list) -> tuple:
        while 0 in lista1:
            lista2.pop(lista1.index(0))
            lista1.remove(0)
        return lista1, lista2

    def get_alpha(self, id: int, li_fit: float, ls_fit: float, name: str) -> tuple:
        # Configuramos el AlphaCalculator
        self.alpha_calculator = AlphaCalculator(li_fit, ls_fit)
        data_path = f'{self._edgePath}{id}'

        # Calculamos alpha y obtenemos datos para la gráfica
        alpha, x0, y0, model = self.alpha_calculator.calculate_alpha(data_path)
        values = [name, id, alpha]

        self._alpha.append(alpha)
        self._values.append(values)

        # Devolver los valores necesarios para graficar
        return x0, y0, model

    def plot_alpha_distribution(self, x0, y0, model, li_fit, ls_fit, xlimi, xlims, color, name):
        # Plot degree distribution
        a = np.linspace(li_fit, ls_fit, 10)
        
        plt.figure(figsize=(6, 4))
        plt.plot(x0, y0, color=color, linewidth=0, marker="P", markersize=5, label="data")
        plt.plot(a, (a)*(model.params[1]) + model.params[0]*1., color="k", lw=3, 
                 label=r"fit ($\alpha_0={}$)".format(-np.round(model.params[1], 2)))
        plt.xlabel(r'$\log_{10}(k)$ (Degree)')
        plt.ylabel(r'$\log_{10} P(k)$')
        plt.title('Degree Distribution {}'.format(name))
        plt.legend()
        plt.xlim(xlimi, xlims)
        plt.legend(title=r"$P(k)\sim x^{-\alpha_0}$")
        plt.grid(alpha=0.5)
        plt.show()
        #prueba de commit

if __name__ == '__main__':
    intento = GraphAnalyzer()
    intento.type = 'hol'
    print(intento.alpha)

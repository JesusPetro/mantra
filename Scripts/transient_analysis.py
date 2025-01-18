#==============
import matplotlib.pyplot as plt
import pandas as pd
import networkx as nx
import numpy as np
import os
import statsmodels.api as sm
from visibility_graph import visibility_graph

class TransientDataLoader:
    """
    A class to load and manage transient data files.

    This class handles setting up file paths, creating directories,
    and loading transient data from CSV files.

    Attributes
    ----------
    _path : str
        The base path for storing transient data.
    _edgePath : str
        The path where edge list files will be stored.
    _pdfPath : str
        The path where PDF files will be stored.
    _pathData : str
        The path of the specific CSV file for the transient type.
    _type : str
        The type of transient data (e.g., 'AGN').
    transient : pd.DataFrame
        A DataFrame to store the loaded transient data.

    Methods
    -------
    set_and_create_path():
        Sets file paths and creates directories if they do not exist.
    read_dataframe():
        Loads the transient data from the specified CSV file into a DataFrame.
    """

    def __init__(self, type=''):
        """
        Constructs all the necessary attributes for the TransientDataLoader object.

        Parameters
        ----------
        type : str, optional
            The type of transient data (default is '').
        """
        self._path: str = ''
        self._edgePath: str = ''
        self._pdfPath: str = ''
        self._pathData: str = ''
        self.transient: pd.DataFrame = None

        self.type: str = type

    
    @property
    def type(self):
        """
        Gets the type of transient data.

        Returns
        -------
        str
            The type of transient data.
        """
        return self._type

    @property
    def edgePath(self):
        """
            Gets the EdgePath of transient data.

            Returns
            -------
            str
                The EdgePath of transient data.
        """
        return self._edgePath


    @type.setter
    def type(self, type):
        """
        Sets the type of transient data and updates the file paths.

        Parameters
        ----------
        type : str
            The type of transient data to be set.
        """

        self._type = type
        self.set_and_create_path()
        self.read_dataframe()
        # self.edgeList()


    def set_and_create_path(self):
        """
        Sets up file paths and creates necessary directories for transient data.

        Paths for data, edge lists, and PDFs are set and created based on the type of transient.
        """
        self._pathData = f'../data/csv/{str(self._type)}.csv'
        self._path = f'../data/transient/{str(self._type)}/'
        self._edgePath = f'{self._path}edgeList/'
        self._pdfPath = f'{self._path}pdf'
        #TODO: carpeta de natural y horizontal

        # Create directories if they do not exist
        directories = [self._path, self._edgePath, self._pdfPath]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def read_dataframe(self):
        """
        Loads the transient data from the CSV file into a pandas DataFrame.

        The path of the CSV file is determined based on the transient type.
        """
        self.transient = pd.read_csv(self._pathData)

    def edgeList(self):
        """
        Generates a visibility graph from the transient data and writes it to an edge list file.

        This method retrieves the 'Mag' (magnitude) values for a specific 'ID' from the transient data,
        constructs a visibility graph from those values, and saves the resulting graph as an edge list
        to the specified file path.

        The visibility graph is generated using the function `visibility_graph`, which is expected to
        convert the provided data into a NetworkX graph. The resulting graph is then saved as an edge list.

        Raises
        ------
        KeyError
            If the 'ID' or 'Mag' columns are not present in the DataFrame.
        ValueError
            If the visibility graph cannot be generated due to invalid data.
        
        Notes
        -----
        - The method assumes that the `visibility_graph` function is already defined and returns a NetworkX graph.
        - The output is written to `self._edgePath`, which must be a valid file path.

        Example
        -------
        loader = TransientDataLoader(type='AGN')
        loader.edgeList()

        """

    # Verify the required columns are in the DataFrame
        if 'ID' not in self.transient.columns or 'Mag' not in self.transient.columns:
            raise KeyError("DataFrame must contain 'ID' and 'Mag' columns.")


        unique_ids = self.transient['ID'].unique()
        
        
        for id in unique_ids :
            vec_id = self.transient[self.transient['ID'] == id]['Mag']
            graph_id = visibility_graph(vec_id)
            
            try:
                nx.write_edgelist(graph_id, f'{self._edgePath}/{id}')
                print(f'Edge list written for ID {id} at {self._edgePath}')
                       
            except Exception as e:
                print(f'Failed to write edge list for ID {id}: {str(e)}')

class VisibilityGraphAnalyzer:
    """
    A class to analyze visibility graphs and calculate the alpha parameter.

    This class calculates alpha based on the degree distribution of a visibility graph
    and provides functionality to plot the distribution.

    Attributes
    ----------
    _alpha : list
        A list to store alpha values calculated for different graphs.
    _values : list
        A list to store analysis results, including graph name, ID, and alpha value.
    _type : str
        The type of the visibility graph (e.g., 'horizontal', 'vertical').
    _id : int
        An identifier for the graph being analyzed.
    li_fit : float
        The lower bound for the degree distribution fit.
    ls_fit : float
        The upper bound for the degree distribution fit.

    Methods
    -------
    get_alpha(edgePath: str, id: int, name: str) -> tuple:
        Calculates the alpha parameter for a visibility graph.
    plot_alpha_distribution(x0, y0, model, xlimi, xlims, color, name):
        Plots the degree distribution and fitted alpha line.
    """
    #TODO: ver lo de li_fit y ls_fit
    def __init__(self, type: str ='', li_fit: float= 0, ls_fit: float = 2):
        """
        Constructs all the necessary attributes for the VisibilityGraphAnalyzer object.

        Parameters
        ----------
        type : str, optional
            The type of the visibility graph (default is '').
        li_fit : float, optional
            The lower bound for fitting the degree distribution (default is 0).
        ls_fit : float, optional
            The upper bound for fitting the degree distribution (default is 0).
        """
        self._alpha: list = []
        self._values: list = []
        self._x0 = []
        self._y0 = []


        self._id = 0
        self._model = 0
        
        self.li_fit: float = li_fit
        self.ls_fit: float = ls_fit

        self._type: str = type

    @property
    def alpha(self):
        """
        Gets the list of calculated alpha values.

        Returns
        -------
        list
            The list of alpha values.
        """
        return self._alpha
    
    
    @property
    def id (self):
        """
        Gets the id of transient data.

        Returns
        -------
        str
            The id of transient data.
        """
        return self._id
    
    
    @property
    def type(self):
        """
        Gets the type of transient data.

        Returns
        -------
        str
            The type of transient data.
        """
        return self._type
    
    @type.setter
    def type(self, type):
        """
        Sets the type of transient data and updates the file paths.

        Parameters
        ----------
        type : str
            The type of transient data to be set.
        """

        self._type = type

    @property
    def values(self):
        """
        Gets the list of analysis values (graph name, ID, and alpha).

        Returns
        -------
        list
            The list of analysis values.
        """
        return self._values

    @property 
    def x0(self):
        """
        Gets the list of x0 values.

        Returns
        -------
        list
            The list of x0 values.
        """
        return self._x0
    
    @property 
    def y0(self):
        """
        Gets the list of y0 values.

        Returns
        -------
        list
            The list of y0 values.
        """
        return self._y0

    def remove_zeros (self, lista1, lista2):
        """
        Removes zeros from two related lists. The elements in `list2` are removed according to the indexes of the zeros in `list1`. 

        Parameters
        ----------
        list1 : list
            Main list from which zeros will be removed.
        list2 : list
            Secondary list from which corresponding elements will be removed.

        Returns
        -------
        tuple
            The filtered lists without zeros in `list1`.
        """

        while 0 in lista1:
            lista2.pop(lista1.index(0))
            lista1.remove(0)
        return lista1, lista2 

    def get_alpha(self, edgePath: str, id: int, name: str) -> tuple:
        """
        Calculates the alpha parameter for a visibility graph.

        Parameters
        ----------
        edgePath : str
            The file path to the edge list of the graph.
        id : int
            The ID of the graph being analyzed.
        name : str
            The name of the graph or dataset.

        Returns
        -------
        tuple
            A tuple containing the degree (x0), degree distribution (y0), and the fitted model.
        """
        try:
            data_path = f'{edgePath}{id}'
            # print(data_path)
            G = nx.read_edgelist(data_path, nodetype=int)
        
            degree_count = nx.degree_histogram(G)
            degrees = list(range(0, len(degree_count)))
            degree_count, degrees = self.remove_zeros(degree_count, degrees)
            
            degree_distribution = [count / float(sum(degree_count)) for count in degree_count]
            self._x0, self._y0 = np.array(np.log10(degrees)),np.array(np.log10(degree_distribution))

            x, y = self._x0[(self._x0 >= self.li_fit) & (self._x0 <= self.ls_fit)], self._y0[(self._x0 >= self.li_fit) & (self._x0 <= self.ls_fit)]
            x = sm.add_constant(x)
            self._model = sm.OLS(y, x).fit()


            alpha = -np.round(self._model.params[1], 2)

            self._alpha.append(alpha)
            self._values.append([name, id, alpha])
            # return alpha
        
        except FileNotFoundError:
            print(f'Error: File not found {data_path}')
            return None

        # return self._x0, self._y0, self._model
    def plot_alpha_distribution(self, xlimi, xlims, color, name, ax, save_path=None):
        """
        Plots the degree distribution along with the fitted alpha line.
        Optionally saves the plot to a file.

        Parameters
        ----------
        xlimi : float
            The lower limit for the x-axis.
        xlims : float
            The upper limit for the x-axis.
        color : str
            The color for the plot.
        name : str
            The name of the graph or dataset.
        ax : matplotlib.axes._axes.Axes
            The axis to plot on.
        save_path : str, optional
            The file path to save the plot (default is None, which means the plot is shown instead of saved).
        """
        a = np.linspace(self.li_fit, self.ls_fit, 10)
        # plt.figure(figsize=(6, 4))
        ax.plot(self._x0, self._y0, color=color, linewidth=0, marker="P", markersize=5, label="data")
        ax.plot(a, (a) * (self._model.params[1]) + self._model.params[0], color="k", lw=3,
                label=r"fit ($\alpha_0={}$)".format(-np.round(self._model.params[1], 2)))
        ax.xlabel(r'$\log_{10}(k)$ (Degree)')
        ax.ylabel(r'$\log_{10} P(k)$')
        ax.title(f'Degree Distribution for {name}')
        ax.xlim(xlimi, xlims)
        ax.grid(alpha=0.5)
        ax.legend()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    """ intento = TransientDataLoader(type='AGN')
    print(intento.transient)
    print(len(intento.transient['ID'].unique()))
    print(intento.transient['ID'].unique()) """
    

    intento = VisibilityGraphAnalyzer('AGN', 0.8, 1.41)
    intento.get_alpha('../data/transient/AGN/edgeList/', 1202251320404143265, 'AGN')
    


    # fig, (aux1, aux2) = plt.subplots(1,2, figsize = (6,4))  
    plt.subplot(1,3,1)
    intento.plot_alpha_distribution(0.26, 1.78, 'red', 'AGN', plt)    
    plt.subplot(1,3,2)
    intento.plot_alpha_distribution(0.26, 1.78, 'red','AGN', plt)
    plt.tight_layout()
    plt.show()

    

#TODO: 1302141150504102321
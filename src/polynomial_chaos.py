import openturns as ot
import numpy as np
import pandas as pd
import  openturns.viewer as viewer
from matplotlib import pylab as plt


ACCEPTED_DISTRIBUTIONS = ["Normal", "Uniform"]
DISTR_KEY = 'distribution'
PARAM_KEY = 'parameters'


class PCArchitect:
    
    def __init__(self, variables: dict) -> None:
        """
        Parameters should have the following construction.
        {
            "name1": {distribution: "normal", parameters: {"mu": 342, "var": 4453}},
            "name2": {distribution: "uniform", parameters: {"min": 432, "max": 4324}}
        }

        The initialization creates the composed input distribution and the corresponding basis.
        """
        self.DISTR_KEY = 'distribution'
        self.PARAM_KEY = 'parameters'
        self.variables = {k: self._recognize_distr(v) for k,v in variables.items()}
        self.distribution = ot.ComposedDistribution([v for v in self.variables.values()])
        self.input_dimension = self.distribution.getDimension()
        
        # Create the family of polynomials for this task
        polyColl = ot.PolynomialFamilyCollection(self.input_dimension)
        for i in range(self.input_dimension):
            marginal = self.distribution.getMarginal(i)
            polyColl[i] = ot.StandardDistributionPolynomialFactory(marginal)

        q = 0.5
        enumerateFunction = ot.HyperbolicAnisotropicEnumerateFunction(self.input_dimension, q)
        # Create the basis for the polynomials.
        self.multivariate_basis = ot.OrthogonalProductPolynomialFactory(
            polyColl, enumerateFunction)


    def __eq__(self, __o: object) -> bool:
        return type(__o) is PCArchitect and __o.distribution == self.distribution

    def get_experimental_design(self, sample_size, dataframe_only=False):
        # Return the sampling points as pandas dataframe.
        experiment = ot.LHSExperiment(self.distribution, sample_size)
        samples, weights = experiment.generateWithWeights()
        samples_df = pd.DataFrame(np.asarray(samples), columns=self.variables.keys())
        weights = np.asarray(weights)
        if dataframe_only:
            return samples_df
        return samples, samples_df, weights

    def predict(self, input_samples: pd.DataFrame, x_col: str, sweep_col: str):
        # Random variable names are in `self.variables`. 
        # `x_col` represents a name for a deterministic variable
        # We need to search in available models for the value of `x_col` as close as possible
        # to the values that we have in the available models.
        pass

    def compute_pc_expansion(self, input_samples: pd.DataFrame, output_samples: pd.DataFrame, max_total_degree, x_col, sweep_col):
        if np.any(np.isin(sweep_col, input_samples.columns)):
            if input_samples.index.name is None:
                input_samples = input_samples.set_index(sweep_col).sort_index()
            elif input_samples.index.name != sweep_col:
                input_samples = input_samples.reset_index().set_index(sweep_col).sort_index()
            input_samples = np.asarray(input_samples)
        else:
            # Assume that `input_samples` are sorted correctly.
            input_samples = np.asarray(input_samples)
            pass

        if output_samples.index.name is None:
            output_samples = output_samples.set_index(sweep_col).sort_index()
        elif output_samples.index.name != sweep_col:
            output_samples = output_samples.reset_index().set_index(sweep_col).sort_index()
        elif output_samples.index.name == sweep_col:
            output_samples = output_samples.sort_index()
        output_samples = output_samples.set_index(x_col).sort_index()
        
        unique_indices = output_samples.index.unique()
        pclist = [ot.metamodel.FunctionalChaosResult()] * len(unique_indices)
        for i, t in enumerate(unique_indices):
            partdf = np.asarray(output_samples.loc[t])
            pc_expansion = self.compute_sparse_pc_expansion(input_samples, partdf, max_total_degree)
            pclist[i] = pc_expansion
        return pclist

    def compute_sparse_pc_expansion(self, input_samples, output_samples, max_total_degree):
        """
        Computes the sparse expansion given `input_samples` and `output_samples`
        """
        output_samples = np.asarray(output_samples)
        selection_algorithm = ot.LeastSquaresMetaModelSelectionFactory()
        least_squares = ot.LeastSquaresStrategy(input_samples, output_samples, selection_algorithm)
        enumfunc = self.multivariate_basis.getEnumerateFunction()
        degree = enumfunc.getStrataCumulatedCardinal(max_total_degree)
        basis_strategy = ot.FixedStrategy(self.multivariate_basis, degree)
        pc_algo = ot.FunctionalChaosAlgorithm(input_samples, output_samples, self.distribution, basis_strategy, least_squares)
        pc_algo.run()
        pc_expansion = pc_algo.getResult()
        return pc_expansion

    @staticmethod
    def interpolate_df_n(df: pd.DataFrame, sweep_col, x_col, values_range, no_interpolated, indexed=False):
        # TODO: Optimize
        assert type(values_range) is list and len(values_range)==2
        no_interpolated = int(no_interpolated) # Cast to integer
        knots = np.linspace(values_range[0], values_range[1], no_interpolated) # Knots for interpolations
        
        # Set index to `sweep_col` of not done already
        if df.index.name is None:
            df = df.set_index(sweep_col)
        elif df.index.name != sweep_col:
            df = df.reset_index().set_index(sweep_col) 
        chosen_cols = df.columns[df.columns != x_col] # Get names of all columns except the x column
        no_sweeps = df.index.unique()
        xpdf = df[x_col]
        
        dflist = [] # Empty list which will hold df's
        for sweep_no in no_sweeps:
            try:
                xp = np.asarray(xpdf.loc[sweep_no].values) # Make sure this converts to array
                func = lambda yp: np.interp(knots, xp, yp)
                newdf = df.loc[sweep_no, chosen_cols].reset_index()[chosen_cols]
                newdf = pd.DataFrame({
                    name: func(np.asarray(newdf[name].values)) for name in newdf.columns
                })
                newdf[x_col] = knots # Add the new x-axis column 
                newdf[sweep_col] = sweep_no # Add the sweep to the column
                dflist.append(newdf)
            except Exception as e:
                print(e)
                pass
        
        interpdf = pd.concat(dflist)
        if indexed:
            interpdf = interpdf.set_index(sweep_col)
            
        return interpdf

    @staticmethod
    def _recognize_distr(var: dict):
        distr = var[DISTR_KEY]
        parameters = var[PARAM_KEY]
        if distr.upper() == 'NORMAL':
            # For now let's assume that the parameters are given in a correct way.
            return ot.Normal(parameters['mu'], parameters['var'])
        elif distr.upper() == 'UNIFORM':
            return ot.Uniform(parameters['min'], parameters['max'])
        elif distr.upper() == 'LOGNORMAL':
            return ot.LogNormal(parameters['muLog'], parameters['sigmaLog'], parameters['gamma'] if 'gamma' in parameters else 0.0)
        else:
            raise NotImplementedError('Other distribution are not implemented yet.')



if __name__=='__main__':



    vars = {
        "Ts": {
            "distribution": "normal",
            "parameters": {
                "mu": 3,
                "var": 0.3
            }
        },
        "dV": {
            "distribution": "uniform",
            "parameters": {
                "min": 0.5,
                "max": 1.2
            }
        }
    } 

    # Create pc instance
    pcarch = PCArchitect(vars)

    sample_size = 3
    pts, varsdf, w = pcarch.get_experimental_design(sample_size=sample_size)
    print(varsdf)
    # To the same points apply two different functions
    fun1 = lambda t, x, y: t**2 + 0.2*x**2 + 0.4*y**3
    fun2 = lambda t, x, y: t**2 + np.sin(x) - 0.4*y**3

    # I need to simulate the `sample_size` times I am getting a result. The time vector for each of these results can be different.
    start, stop = 0.1, 0.3 # Time vector bounds.
    low, high = 3, 5 # number of possible lengths of the time vector
    ntime = np.random.randint(low, high+1, sample_size)
    dflist = []
    for i, ind in enumerate(varsdf.index):
        time = np.linspace(start, stop, ntime[i])
        partdf = varsdf.loc[ind]
        partdf = pd.DataFrame({
            'time': time,
            'fun1': fun1(time, partdf['Ts'], partdf['dV']),
            'fun2': fun2(time, partdf['Ts'], partdf['dV']),
            'sweep': i
        })
        dflist.append(partdf)

    df = pd.concat(dflist)

    aggdf = df[['time', 'sweep']].groupby('sweep').agg(
        func = ['count', 'min', 'max'],axis=0
        )['time']

    maxtime = np.max(aggdf['max'])
    mintime = np.min(aggdf['min'])
    meancount  = np.int64(np.ceil(np.mean(aggdf['count']))) # Cast to integer

    interpolated = PCArchitect.interpolate_df_n(df, 'sweep', 'time', [mintime, maxtime], meancount, indexed=True)
    print(interpolated)

    # pcarc = PCArchitect({
    #     'v1': {
    #         'distribution': 'normal',
    #         'parameters': {
    #             'mu': 2,
    #             'var': 0.1
    #         }
    #     },
        
    #     'v2': {
    #         'distribution': 'uniform',
    #         'parameters': {
    #             'min': 0,
    #             'max': 3
    #         }
    #     }
    # })

    # N = 20
    # points, df, weights = pcarc.get_experimental_design(N)

    # # Create an inline function 
    # fun1 = lambda x, y: x**2 + 3*y**2
    # fun2 = lambda x, y: 1.2*x**2 + 3*y**3


    # # Create a new output. This corresponds to one `sweep`
    # new = fun1(df['v1'], df['v2'])
    # # new.values should be numpy array
    # pcalgo = pcarc.compute_sparse_pc_expansion(points, new.values, 3)
    # metamodel = pcalgo.getMetaModel()

    # points, _, _ = pcarc.get_experimental_design(1000)
    # metaresult = metamodel(points)
    # graph = ot.HistogramFactory().build(metaresult).drawPDF()
    # view = viewer.View(graph)
    # plt.show()


    # There also has to be some kind of validation metrics.


    # # Test for the interpolation
    # df = pd.DataFrame({
    #     'time': [1, 2, 3, 4, 1, 2, 3, 2, 3, 4],
    #     'value1': [1, 2, 3, 4, 1, 2, 3, 2, 3, 4],
    #     'value2': [1.5, 2.5, 3.5, 4.5, 1.5, 2.5, 3.5, 2.5, 3.5, 4.5],
    #     'sweep': [0, 0, 0, 0, 1, 1, 1, 2, 2, 2]
    # })

    # interpolated = pcarc._interpolate_df(df, sweep_col='sweep', x_col='time')
    # print(interpolated)
    # print('\n')
    # print(interpolated.loc[0:2, 'value1':'sweep'])

import openturns as ot
import numpy as np
import pandas as pd
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

    def predict(self, input_samples: pd.DataFrame, pc_expansion, sweep_col: str, x_col=None):
        if type(pc_expansion) is list and x_col is not None:
            return self._predict_batch(input_samples, pc_expansion, x_col, sweep_col)
        elif type(pc_expansion) is ot.FunctionalChaosResult:
            return self._predict_single(input_samples, pc_expansion, sweep_col)
        else:
            raise ValueError("Improper types for `predict`.")


    def _predict_single(self, input_samples: pd.DataFrame, pc_expansion: ot.metamodel.FunctionalChaosResult, sweep_col: str):
        if np.any(np.isin(sweep_col, input_samples.columns)):
            if input_samples.index.name is None:
                input_samples = input_samples.set_index(sweep_col).sort_index()
            elif input_samples.index.name != sweep_col:
                input_samples = input_samples.reset_index().set_index(sweep_col).sort_index()
            input_samples = np.asarray(input_samples)
        else:
            input_samples = np.asarray(input_samples)
        metamodel = pc_expansion.getMetaModel()
        newoutput = metamodel(input_samples)
        newoutput_df = pd.DataFrame(np.asarray(newoutput))
        return newoutput_df

    def get_sobol_indices(self, pc_expansion):
        sobolIndices = ot.FunctionalChaosSobolIndices(pc_expansion)
        return sobolIndices

    def nonzero_variables(self, sobolIndices, marginals=None):
        pc_expansion = sobolIndices.getFunctionalChaosResult()
        metamodel = pc_expansion.getMetaModel()
        dimension = metamodel.getInputDimension()
        if marginals is None:
            output_dim = metamodel.getOutputDimension()
            marginals = range(output_dim)
        outputDescription = metamodel.getOutputDescription()
        outNonzero = {}
        for m in marginals:
            first_order = [sobolIndices.getSobolIndex(i, m) for i in range(dimension)]
            description = metamodel.getInputDescription()
            outNonzero[outputDescription[m]] = {description[i]: first_order[i] for i in range(len(first_order)) if first_order[i] > 0}
        return outNonzero
        

        

    def hist(self, pc_expansion, n_samples):
        newpts, _,_ = self.get_experimental_design(n_samples)
        metamodel = pc_expansion.getMetaModel()
        newoutput = metamodel(newpts)
        columns = metamodel.getOutputDescription()
        output_df = pd.DataFrame(np.asarray(newoutput), columns=columns)
        h = output_df.hist(bins=20, density=True)
        return h


    def _predict_batch(self, input_samples: pd.DataFrame, pc_expansions: list, x_col: str, sweep_col: str):
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

    def compute_sparse_pc_expansion(self, input_samples, output_samples, max_total_degree, description=None):
        """
        Computes the sparse expansion given `input_samples` and `output_samples`
        """
        # Set description
        output_samples = np.asarray(output_samples)
        selection_algorithm = ot.LeastSquaresMetaModelSelectionFactory()
        least_squares = ot.LeastSquaresStrategy(input_samples, output_samples, selection_algorithm)
        enumfunc = self.multivariate_basis.getEnumerateFunction()
        degree = enumfunc.getStrataCumulatedCardinal(max_total_degree)
        basis_strategy = ot.FixedStrategy(self.multivariate_basis, degree)
        pc_algo = ot.FunctionalChaosAlgorithm(input_samples, output_samples, self.distribution, basis_strategy, least_squares)
        pc_algo.run()
        pc_expansion = pc_algo.getResult()
        if description is not None:
            metamodel = pc_expansion.getMetaModel()
            metamodel.setDescription(description) 
            pc_expansion.setMetaModel(metamodel)
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
    print("Polynomial Chaos")
import openturns as ot
import numpy as np
from openturns.statistics import CovarianceBlockAssemblyFunction
import pandas as pd
from scipy import interpolate


class PCArchitect:
    
    def __init__(self, variables: dict) -> None:
        """
        Parameters should have the following construction.
        {
            "name1": {distribution: "normal", parameters: {"mu": 342, "var": 4453}},
            "name2": {distribution: "uniform", parameters: {"min": 432, "max": 4324}}
        }
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

        # Maximum number of polynomials to preserve.
        max_degree = 5
        max_polys = enumerateFunction.getStrataCumulatedCardinal(max_degree)

        # Truncature basis strategy
        significance_factor = 1e-4
        most_significant = 120
        truncature_basis_strategy = ot.CleaningStrategy(
            self.multivariate_basis, max_polys, most_significant, significance_factor, True)
        self.truncature_basis_strategy = truncature_basis_strategy

    def _get_experimental_design(self, sample_size):
        # Return the sampling points as pandas dataframe.
        experiment = ot.LHSExperiment(self.distribution, sample_size)
        samples, weights = experiment.generateWithWeights()
        samples_df = pd.DataFrame(np.asarray(samples), columns=self.variables.keys())
        weights = np.asarray(weights)
        return samples, samples_df, weights
    
    def _interpolate_df(self, df: pd.DataFrame, sweep_col, x_col):
        """
        In cases `df` has different lengths of the data between different factors
        an interpolation is required to be able to perform PC on the data.
        `sweep_col` is the factor column
        `x_col` is the axis column (for instance time or frequency)
        """
        assert isinstance(sweep_col, str) and sweep_col in df.columns
        aggregated = df.groupby(
                sweep_col
            ).agg(
                no_samples=pd.NamedAgg(column=sweep_col, aggfunc=len)
            ).sort_values(
                by='no_samples', ascending=False
            )
        interpolant    = aggregated.index[0]
        interpolatable = aggregated.index[1:]
        # Base column for performing the interpolation
        base_df = df[df[sweep_col] == interpolant]
        blen = len(base_df)
        dfs = [self._interpolate_batch_df(
            df, i1, sweep_col, x_col,
            base_df[x_col].values,
            df.columns[~df.columns.isin([sweep_col, x_col])],
            range((idx+1)*blen, (idx+2)*blen),
            {"s": 0, "k":1, "der":0})
            for idx, i1 in enumerate(interpolatable)]
        dfs.insert(0, base_df)
        return pd.concat(dfs)
            
                
    def _interpolate_batch_df(self, df, i1, sweep_col, x_col, xnew, columns, index, params):
        batch_df = df[df[sweep_col] == i1]
            # Loop through the columns and perform interpolation to each of them.
        batch_df = pd.DataFrame({
            column: self._interpolate(
                batch_df[x_col].values, batch_df[column].values, xnew, params) 
            for column in columns},
            index=index)
        batch_df[x_col] = xnew
        batch_df[sweep_col] = i1
        return batch_df
    

    def _interpolate(self, xold, yold, xnew, params):
        tck = interpolate.splrep(xold, yold, s=params['s'], k=params['k'])
        ynew = interpolate.splev(xnew, tck, der=params['der'])
        return ynew


    def _create_pc_expansion(self, input_samples, output_samples):
        pass


    def _recognize_distr(self, var: dict):
        distr = var[self.DISTR_KEY]
        parameters = var[self.PARAM_KEY]
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
    
    pcarc = PCArchitect({
        'v1': {
            'distribution': 'normal',
            'parameters': {
                'mu': 2,
                'var': 0.1
            }
        },
        
        'v2': {
            'distribution': 'uniform',
            'parameters': {
                'min': 0,
                'max': 3
            }
        }
    })

    # Test for the interpolation
    df = pd.DataFrame({
        'time': [1, 2, 3, 4, 1, 2, 3, 2, 3, 4],
        'value1': [1, 2, 3, 4, 1, 2, 3, 2, 3, 4],
        'value2': [1.5, 2.5, 3.5, 4.5, 1.5, 2.5, 3.5, 2.5, 3.5, 4.5],
        'sweep': [0, 0, 0, 0, 1, 1, 1, 2, 2, 2]
    })

    interpolated = pcarc._interpolate_df(df, sweep_col='sweep', x_col='time')
    print(interpolated)
    print('\n')
    print(interpolated.loc[0:2, 'value1':'sweep'])

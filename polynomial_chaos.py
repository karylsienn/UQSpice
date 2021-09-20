import openturns as ot
from openturns.dist_bundle2 import LogNormal
from openturns.dist_bundle3 import Uniform



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
        self.multivariate_basis = ot.OrthogonalProductPolynomialFactory(polyColl, enumerateFunction)

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
        # 
        experiment = ot.LHSExperiment(self.distribution, sample_size)
        samples, weights = experiment.generateWithWeights()
        return samples, weights


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

    print(pcarc._get_experimental_design(5))
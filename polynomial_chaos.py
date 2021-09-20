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
        self.variables = {k: self.__recognize_distr(v) for k,v in variables.items()}
        self.distribution = ot.ComposedDistribution([v for v in self.variables.values()])
        self.dimension = self.distribution.getDimension()
    

    def __recognize_distr(self, var: dict):
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
                'mu': 0.1,
                'var': 4
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

    print(pcarc.variables)
    print(pcarc.distribution)
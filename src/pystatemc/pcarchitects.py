import openturns as ot
import pandas as pd
import numpy as np


DISTR_KEY = 'distribution'
PARAM_KEY = 'parameters'
ACCEPTED_DISTRIBUTIONS = ['NORMAL', 'UNIFORM', 'BETA', 'GAMMA']


class ExperimentalDesigner:

    def __init__(self, variables: dict):
        self.variables = {k: self._recognize_distributions(v) for k, v in variables.items()}
        self.distribution = ot.ComposedDistribution([v for v in self.variables.values()])
        self.input_dimension = self.distribution.getDimension()

    def get_lhs_design_numpy(self, sample_size: int):
        design = self._get_lhs_design(sample_size)
        return np.asarray(design)

    def get_lhs_design_pandas(self, sample_size: int):
        design = self._get_lhs_design(sample_size)
        return pd.DataFrame(np.asarray(design), columns=self.variables.keys())

    def _get_lhs_design(self, sample_size: int):
        experiment = ot.LHSExperiment(self.distribution, sample_size)
        samples = experiment.generate()
        return samples

    @staticmethod
    def _recognize_distributions(var: dict):
        distr = var[DISTR_KEY]
        if distr not in ACCEPTED_DISTRIBUTIONS:
            raise ValueError(f"The only accepted distributions are: {', '.join(ACCEPTED_DISTRIBUTIONS)}.")

        parameters = var[PARAM_KEY]
        if distr.upper() == 'NORMAL':
            # For now let's assume that the parameters are given in a correct way.
            return ot.Normal(parameters['mu'], parameters['var'])
        elif distr.upper() == 'UNIFORM':
            return ot.Uniform(parameters['min'], parameters['max'])
        elif distr.upper() == 'BETA':
            return ot.Beta(parameters['a'], parameters['b'])
        elif distr.upper() == 'GAMMA':
            return ot.Gamma(parameters['alpha'], parameters['beta'])
        else:
            raise NotImplementedError('Other distributions are not implemented yet.')


import openturns as ot
import pandas as pd
import numpy as np
from typing import List


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
        distr = var[DISTR_KEY].upper()

        if distr not in ACCEPTED_DISTRIBUTIONS:
            raise ValueError(f"The only accepted distributions are: {', '.join(ACCEPTED_DISTRIBUTIONS)}.")

        parameters = var[PARAM_KEY]
        if distr == 'NORMAL':
            # For now let's assume that the parameters are given in a correct way.
            return ot.Normal(parameters['mu'], parameters['var'])
        elif distr == 'UNIFORM':
            return ot.Uniform(parameters['min'], parameters['max'])
        elif distr == 'BETA':
            return ot.Beta(parameters['a'], parameters['b'])
        elif distr == 'GAMMA':
            return ot.Gamma(parameters['alpha'], parameters['beta'])
        else:
            raise NotImplementedError('Other distributions are not implemented yet.')


class PCArchitect:

    def __init__(self, variables: dict):
        self.pc_expansion = None
        self.experimental_designer = ExperimentalDesigner(variables)
        self.input_dimension = self.experimental_designer.input_dimension

        poly_coll = ot.PolynomialFamilyCollection(self.input_dimension)
        for i in range(self.input_dimension):
            marginal = self.experimental_designer.distribution.getMarginal(i)
            poly_coll[i] = ot.StandardDistributionPolynomialFactory(marginal)

        q = 0.5
        enumerate_function = ot.HyperbolicAnisotropicEnumerateFunction(self.input_dimension, q)
        self.multivariate_basis = ot.OrthogonalProductPolynomialFactory(
            poly_coll, enumerate_function
        )

    def get_mean(self, pc_expansion: List[ot.metamodel.FunctionalChaosResult] = None) -> pd.DataFrame:
        if not pc_expansion and not self.pc_expansion:
            raise ValueError("There is not Polynomial Chaos Expansion to compute the mean.")
        elif pc_expansion:
            # Use the provided list of PC expansions to provide the means.
            means = [pc.getCoefficients()[0] for pc in pc_expansion]
            description = pc_expansion[0].getMetaModel().getDescription()
        else:
            # Use the last created PC expansion
            means = [pc.getCoefficients()[0] for pc in self.pc_expansion]
            description = self.pc_expansion[0].getMetaModel().getDescription()
        means_pd = pd.DataFrame(means, columns=description)
        return means_pd

    def get_confidence_interval(self,
                                level='95',
                                pc_expansion: List[ot.metamodel.FunctionalChaosResult] = None):
        if not pc_expansion and not self.pc_expansion:
            raise ValueError("There is no Polynomial Chaos expansion to computer the confidence intervals.")
        elif pc_expansion:
            return PCArchitect._get_confidence_interval(pc_expansion, float(level))
        else:
            return PCArchitect._get_confidence_interval(self.pc_expansion, float(level))

    @staticmethod
    def _get_confidence_interval(pc_expansion: List[ot.metamodel.FunctionalChaosResult],
                                 level=95.0):
        level = float(level)
        assert level in (68.0, 95.0, 99.7)
        if level == 68.0:
            scaling = 1
        elif level == 95.0:
            scaling = 2
        else:
            scaling = 3
        means = [pc.getCoefficients()[0] for pc in pc_expansion]
        sds = [np.sqrt(np.sum(pc[1:] ** 2)) for pc in pc_expansion]
        metamodel = pc_expansion[0].getMetaModel()
        output_description = [metamodel.getOutputDescription().at(i) for i in range(metamodel.getOutputDimension())]
        lower = pd.DataFrame(np.asarray([mu - scaling*sd for mu, sd in zip(means, sds)]),
                             columns=output_description)
        upper = pd.DataFrame(np.asarray([mu + scaling*sd for mu, sd in zip(means, sds)]),
                             columns=output_description)
        return lower, upper

    def get_total_sobol_indices(self, pc_expansion: List[ot.metamodel.FunctionalChaosResult] = None) -> pd.DataFrame:
        """
        frequency_or_time UQ_something UQ_new UQ_C
        1                   0.4         0.5
        2
        """
        if not pc_expansion and not self.pc_expansion:
            raise ValueError("There is no Polynomial Chaos expansions to compute the Sobol indices.")
        elif pc_expansion:
            sobol_indices = [ot.FunctionalChaosSobolIndices(pc) for pc in pc_expansion]
        else:
            sobol_indices = [ot.FunctionalChaosSobolIndices(pc) for pc in self.pc_expansion]
        # Get the total Sobol indices.
        total_sobol_indices = [
            [s.getSobolTotalIndex(m) for m in range(len(self.experimental_designer.variables))
             ] for s in sobol_indices]
        return sobol_indices

    def compute_pc_expansion(self,
                             input_samples: pd.DataFrame,
                             output_samples: pd.DataFrame,
                             max_total_degree=3):
        """
        Computes the (default) Polynomial Chaos Expansion.

        Parameters
        ----------
            * input_samples : DataFrame
                the dataframe of the input samples, with rows indicating "steps"
            * output_samples : DataFrame
                the dataframe of the output samples
            * max_total_degree : int
                the maximum total degree of the expansion

        Raises
        ------
            ValueError
                when the column names of the `input_samples` are not the same as the names of the `variables`

        In case neither column "frequency" not "time" is  present in the `output_samples`,
        number of rows in both `output_samples` and `input_samples` are assumed to be equal.
        The dataframe is supposed to be ordered by the column "step" - such that each row in the input samples
        correspond to one

        """
        input_columns = set(input_samples.columns)
        input_columns_ed = set(self.experimental_designer.variables.keys())
        if len(input_columns - input_columns_ed) > 0 or len(input_columns_ed - input_columns) > 0:
            raise ValueError("Check your input columns.")
        # Check if time or frequency is present in the columns, in case there is set it as index.
        output_columns = output_samples.columns
        if 'time' in output_columns and 'frequency' in output_columns:
            # Only one is allowed.
            raise ValueError("Either 'time' or 'frequency' is allowed, not both.")
        elif 'time' in output_columns or 'frequency' in output_columns:
            x_name = 'time' if 'time' in output_columns else 'frequency'
            output_samples = output_samples.set_index(x_name)
            unique_indices = output_samples.index.unique()
            pc_list = [ot.metamodel.FunctionalChaosResult()] * len(unique_indices)
            for i, t in enumerate(unique_indices):
                part_df = np.asarray(output_samples.loc[t])
                pc_expansion = self._compute_pc_expansion(input_samples=np.asarray(input_samples),
                                                          output_samples=np.asarray(part_df),
                                                          max_total_degree=max_total_degree)
                pc_list[i] = pc_expansion
            self.pc_expansion = pc_list
            return pc_list
        else:
            # TODO: Implement PC in case of .meas statements.
            pass

    def _compute_pc_expansion(self,
                              input_samples,
                              output_samples,
                              max_total_degree=3):
        selection_algorithm = ot.LeastSquaresMetaModelSelectionFactory()
        least_squares = ot.LeastSquaresStrategy(input_samples,
                                                output_samples,
                                                selection_algorithm)
        enumerate_function = self.multivariate_basis.getEnumerateFunction()
        degree = enumerate_function.getStrataCumulatedCardinal(max_total_degree)
        basis_strategy = ot.FixedStrategy(self.multivariate_basis, degree)
        pc_algo = ot.FunctionalChaosAlgorithm(input_samples,
                                              output_samples,
                                              self.experimental_designer.distribution,
                                              basis_strategy,
                                              least_squares)
        pc_algo.run()
        pc_expansion = pc_algo.getResult()
        return pc_expansion



import openturns as ot
import pandas as pd
import numpy as np
from typing import Tuple, Dict

DISTR_KEY = 'distribution'
PARAM_KEY = 'parameters'
ACCEPTED_DISTRIBUTIONS = ['NORMAL', 'UNIFORM', 'BETA', 'GAMMA']


class ExperimentalDesigner:

    def __init__(self, variables: dict):
        self.variables = {k: self._recognize_distributions(v) for k, v in variables.items()}
        self.distribution = ot.ComposedDistribution([v for v in self.variables.values()])
        self.distribution.setDescription([k for k in self.variables.keys()])
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

    def get_mean(self, pc_expansion: Tuple[ot.metamodel.FunctionalChaosResult] = None) -> pd.DataFrame:
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
                                level: str | int | float = '95',
                                pc_expansion: Tuple[ot.metamodel.FunctionalChaosResult] | None = None):
        if not pc_expansion and not self.pc_expansion:
            raise ValueError("There is no Polynomial Chaos expansion to computer the confidence intervals.")
        elif pc_expansion:
            return PCArchitect._get_confidence_interval(pc_expansion, float(level))
        else:
            return PCArchitect._get_confidence_interval(self.pc_expansion, float(level))

    @staticmethod
    def _get_confidence_interval(pc_expansion: Tuple[ot.metamodel.FunctionalChaosResult],
                                 level: float = 95.0) -> Dict[str, pd.DataFrame]:
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
        lower = pd.DataFrame(np.asarray([mu - scaling * sd for mu, sd in zip(means, sds)]),
                             columns=output_description)
        upper = pd.DataFrame(np.asarray([mu + scaling * sd for mu, sd in zip(means, sds)]),
                             columns=output_description)
        return {
            "lower": lower, "upper": upper
        }

    def get_total_sobol_indices(self,
                                pc_expansion: Tuple[ot.metamodel.FunctionalChaosResult] | None = None
                                ) -> Dict[str, pd.DataFrame]:
        """
        Creates and returns the total sobol indices for the Polynomial Chaos Expansion.

        Parameters
        ----------
        pc_expansion : Tuple[openturns.FunctionalChaosResult]
            the tuple of polynomial chaos expansions as returned by `compute_pc_expansion`

        Returns
        -------
        Dict[pandas.DataFrame]
            a dictionary of dataframes consisting the total sobol indices

        In case the pc_expansion is not given, the function uses internal pc_expansion of the PCArchitect instance.
        The format of the returning dictionary is as follows: `{input_var1: DataFrame, input_var2: DataFrame etc.}`
        The rows of the single dataframes correspond to the x-axis and the columns represent the output variables.
        """
        if not pc_expansion and not self.pc_expansion:
            raise ValueError("There is no Polynomial Chaos expansions to compute the Sobol indices.")
        elif pc_expansion:
            sobol_indices = [ot.FunctionalChaosSobolIndices(pc) for pc in pc_expansion]
        else:
            sobol_indices = [ot.FunctionalChaosSobolIndices(pc) for pc in self.pc_expansion]
        metamodel_0 = sobol_indices[0].getFunctionalChaosResult().getMetaModel()
        # Get the dimensions
        input_dimension = metamodel_0.getInputDimension()
        output_dimension = metamodel_0.getOutputDimension()
        # Get the names
        input_description = tuple(str(name) for name in metamodel_0.getInputDescription())
        output_description = tuple(str(name) for name in metamodel_0.getOutputDescription())
        # Get the total Sobol indices.
        total_sobol_indices = np.asarray([
            [[s.getSobolTotalIndex(var_no, marginal_no) for marginal_no in range(output_dimension)]
             for s in sobol_indices]
            for var_no in range(input_dimension)])
        return {
            k: pd.DataFrame(total_sobol_indices[i],
                            columns=output_description) for k, i in zip(
                input_description, range(input_dimension))
        }

    def compute_pc_expansion(self,
                             input_samples: pd.DataFrame,
                             output_samples: pd.DataFrame,
                             max_total_degree=3
                             ) -> Tuple[ot.metamodel.FunctionalChaosResult]:
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
                                                          output_description=tuple(x for x in output_columns if x != x_name),
                                                          max_total_degree=max_total_degree)
                pc_list[i] = pc_expansion

            self.pc_expansion = tuple(pc_list)
            return tuple(pc_list)
        else:
            # TODO: Implement PC in case of .meas statements.
            pass

    def _compute_pc_expansion(self,
                              input_samples: np.array,
                              output_samples: np.array,
                              output_description: Tuple[str],
                              max_total_degree: int
                              ) -> ot.FunctionalChaosResult:
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
        metamodel = pc_expansion.getMetaModel()
        metamodel.setOutputDescription(output_description)
        metamodel.setInputDescription(self.experimental_designer.distribution.getDescription())
        pc_expansion.setMetaModel(metamodel)
        return pc_expansion

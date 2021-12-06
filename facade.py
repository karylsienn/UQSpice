from ltspice_runner import LTSpiceReader, LTSpiceRunner
from polynomial_chaos import ACCEPTED_DISTRIBUTIONS, PCArchitect
from math import factorial


class PCSpice:

    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.ltspice_runner = LTSpiceRunner(file_path)
        self.accepted_distributions = ACCEPTED_DISTRIBUTIONS
        self.pcmodel = None
    
    def get_accepted_distributions(self):
        return self.accepted_distributions
    
    def automatic_pc_model(self, no_simulations: int, vars: dict):
        # Find the largest degree which with a total truncation scheme is possible.
        n, d = len(vars), 1 # Get the number of variables.
        # Total truncation scheme (n+d)!/(n!d!)
        while True:
            nsim = factorial(n+d)/(factorial(n)*factorial(d))
            if nsim >= no_simulations:
                d = d-1 if d > 1 else d
                break
            else:
                d+=1
        
        if d == 1: # Nothing has changed, so apply sparse PC
            self.sparse_pc(no_simulations, vars)
            pass
        else: 
            self.total_trunc_pc(d, vars)
            # Apply the total truncation scheme
            pass
    
    def sparse_pc(self, no_simulations, vars):
        pcmodel = PCArchitect(vars)
        experimental_design = pcmodel.get_experimental_design(no_simulations)
        # Run LTSpice, get output and create PC model.
        pass

    def total_trunc_pc(max_deg, vars):
        pass



def specify_parameters(distr_name):
    distr_name = distr_name.lower()
    if distr_name == "normal":
        parameters = ["Mean", "Variance"]
    elif distr_name == "uniform":
        parameters = ["Min", "Max"]
    else:
        parameters = None
    return parameters
    


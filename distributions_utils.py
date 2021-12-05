from user import ACCEPTED_DISTRIBUTIONS


ACCEPTED_DISTRIBUTIONS = ["Normal", "Uniform"]

def specify_parameters(distr_name):
    distr_name = distr_name.lower()
    if distr_name == "normal":
        parameters = ["Mean", "Variance"]
    elif distr_name == "uniform":
        parameters = ["Min", "Max"]
    else:
        parameters = None
    return parameters



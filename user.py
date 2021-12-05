"""
User commands
"""
import tkinter as tk
from tkinter import filedialog
import os.path
from distributions_utils import specify_parameters, ACCEPTED_DISTRIBUTIONS

class UserBehaviour:
    
    def __init__(self) -> None:
        print("Welcome to UQSpice!")
        while True:
            try:
                uinput = self._print_welcome_menu()
                if uinput == "1":
                    file_path = self._menu_one()
                    if file_path is not None:
                        # Open file and ask about random variables
                        vars = self._random_vars_selection(file_path)
                        print(vars)
                elif uinput == "2":
                    print("Not Implemented yet\n\n")
                elif uinput == "3":
                    print("Not Implemented yet\n\n")
                elif uinput == "4":
                    print("Not Implemented yet\n\n")
                elif uinput == "5":
                    print("Thank you for using UQSpice. See you later!\n\n")
                    break
                else:
                    print("I don't know what you are talking about.\n\n")
                    continue
            except KeyboardInterrupt:
                print("\nSo soon? Ok, see you later.\n")
                break


    def _print_welcome_menu(self):
        print("Menu:")
        print("1. Run LTSpice model")
        print("2. Create a PC model from .log file")
        print("3. Create a PC model from .raw file")
        print("4. Analyze existing UQSpice data")
        print("5. Exit")
        user_input = input("Your choice: ")
        return user_input.strip()


    def _menu_one(self):
        print("\n\nPlease provide a .cir or .net file.")
        print("1. Paste the full path")
        print("2. Select from window gui.")

        while True:
            uinput = input("Your choice: ")
            uinput = uinput.strip()
            if uinput == "1":
                file_path = input("Please provide the path here: ")
                file_path = file_path.strip()
                if os.path.isfile(file_path) and os.path.exists(file_path):
                    print("Verified.")
                    break
                else:
                    print("This is not a file.")
            elif uinput == "2":
                root = tk.Tk()
                root.withdraw()
                file_path = filedialog.askopenfilename()
                file_path = file_path.strip()
                break
            else:
                print("Please, select one of the options.")
        
        
        if file_path is not None:
            print(f"The path to your file is: {file_path}\n")
            return file_path

        return None
    
    def _random_vars_selection(self, path):
        print("Write the names of the random variables separated by space")
        print("Once finished click 'Enter'")
        vars = input("Random variables: ")
        vars = vars.split()
        print("Ok\n")
        print("Now, provide distributions for the random variables.\n")
        # Create a dictionary of random variables
        vars_dict = {var: {'distribution': None, 'parameters': {}} for var in vars}
        for var in vars:
            while True:
                print(f"Variable: {var}")
                print("Select distribution from the following choices:")
                for i, distribution in enumerate(ACCEPTED_DISTRIBUTIONS):
                    print(f"{i+1}. {distribution}")
                selected_distr_no = input("Your choice: ")
                selected_distr = None
                try:
                    selected_distr_no = int(selected_distr_no)
                    if selected_distr_no <= len(ACCEPTED_DISTRIBUTIONS):
                        selected_distr = ACCEPTED_DISTRIBUTIONS[selected_distr_no-1]
                        break
                    else:
                        print("Please select an option.\n")
                except ValueError:
                    print("Please select a valid number.\n")
            if selected_distr is not None:
                vars_dict[var]['distribution'] = selected_distr.lower()
                # Get the parameters of the distribution
                parameters = specify_parameters(selected_distr)
                for param in parameters:
                    while True:
                        param_val = input(f"{param}: ")
                        param_val = param_val.strip()
                        try:
                            param_val = float(param_val)
                            vars_dict[var]['parameters'][param.lower()] = param_val
                            break
                        except ValueError:
                            print("Provide a valid value.\n")
                print("\n")
                        
        return vars_dict
            




        


    


if __name__=="__main__":
    print("Select a .cir or .net file:") # If the selected file is .cir, copy the file and create .net out of it.
    # Finds all the possible variable values in the circuit
    print("Select the random variables. After selecting a variable tell their distribution and parameters.")
    # # Let user further control the PC model if he wishes to.
    print("Do you want to control the PC model?")
    # If yes, ask more if not ask for the maximum allowed simulations
    print("How many simulation do you want to perform?")
    # Find the maximum degree of polynomial which allows to do that with a total truncation scheme, 
    # if such d cannot be found, then use sparse PC with d set to 3.
    # Create the experimental design, add the sweep to the LTspice file.
    # Run LTspice.
    # Read columns from raw file.
    # Are there any .meas or .four commands?
    # If yes, ask which meas commands wants to look at: (all is an option to all)
    # If there no further meas commands and the analysis is based on raw file then ask:
    print("Among the following columns, select those you want to look at.")
    # Select those columns. Interpolate the values (take the interpolation from the transient or ac simulation)
    # Allow user to provide number of points of interpolations.
    print("How many points do you want to interpolate?\n\n")
    # Interpolate
    # Create a PC model.
    # Menu with postprocessing:
    #  1. Plot mean and standard deviation
    #  2. Plot the PC curves (if this is possible)
    #  3. Show the PC coefficients with the basis functions.
    #  4. Evaluate the PC at a given point.
    #  5. Show histogram of a given value 
    

    # There should also be a general menu. The user should be allowed to run simulation but also analyse existing PC models or put existing raw file or log file.
    # 1. Run LTspice model
    # 2. Create PC from .log file
    # 3. Create PC from .raw file
    # 4. Analyze existing PC models.

    userBehaviour = UserBehaviour()
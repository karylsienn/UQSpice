from multiprocessing.sharedctypes import Value
import matplotlib.pyplot as plt
from ltspice_reader import LTSpiceReader
import numpy as np


class Plotter:

    def __init__(self) -> None:
        pass

    def plot_stepped_var(self, ltreader: LTSpiceReader, varname, steps=0):
        steps = np.asarray(steps)
    
        if not hasattr(ltreader, '_data'):
            raise ValueError("Has the LTReader read the results?")
        
        variables = ltreader.header['Variables']
        # Raise error if varname is not a column
        if varname not in variables['Variable'].values:
            raise ValueError("Make sure the variable name matches!")
        # Select the index of the variable
        selectedvar = variables[variables['Variable'] == varname].index.values[0] - 1
        
        if any(steps) < 0:
            raise ValueError("Steps should be positive!")
        elif all(steps) > 0:
            # Silently select only the steps below the maximum number of steps
            max_step = np.max(ltreader._step_indices.index.values)
            steps = steps[steps <= max_step]
        else:
            steps = ltreader._step_indices.index.values

        if ltreader._is_ac_analysis():
            self._plot_stepped_ac(ltreader, varname, selectedvar, steps)
        elif ltreader._is_transient_analysis():
            self._plot_stepped_transient(ltreader, varname, selectedvar, steps)
        

    def _plot_stepped_ac(self, ltreader, varname, selectedvar, steps):
        step_indices = ltreader._step_indices
        _, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        for i in steps:
            start_idx = step_indices.loc[i].start_idx
            stop_idx = step_indices.loc[i].stop_idx
            xvar = ltreader._xvar[start_idx:stop_idx]
            yvar = ltreader._data[start_idx:stop_idx, selectedvar]
            ax1.plot(xvar, 10*np.log10(np.abs(yvar)), linestyle='solid')
            ax2.plot(xvar, 180/np.pi * np.unwrap(np.angle(yvar)), linestyle='dashed')
        
        plt.xscale('log')
        ax1.set_xlabel("Frequency (Hz)")
        ax1.set_ylabel(f"|{varname}| (dB)")
        ax2.set_ylabel(f"angle({varname}) (deg)")
        plt.show()
    
    def _plot_stepped_transient(self, varname, selectedvar, steps):
        pass
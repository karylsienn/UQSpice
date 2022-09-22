
# UQSpice Toolbox
![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)


Uncertainty Quantification toolbox based on openturns and LTspice.
UQSpice is an open-source GUI created using python which uses a LTSpice schematic containing variable names starting with UQ_.
The UQSpice tool uses polynomial chaos and Sobol indices to help identify which of the variables has the most dominant effect on the output of the circuit,
so that later on this component can be shielded from Electromagnetic radiation.


## Table of content
  - [Requirements](#requirements)
  - [GUI guide](#gui-guide)
    - [Opening a schematic](#opening-a-schematic)
      - [Canvas Features](#canvas-features)
    - [Entering Parameters](#entering-parameters)
      - [Running simulations and viewing plots](#running-simulations-and-viewing-plots)
    - [Opening Waveform files](#opening-waveform-files)
    - [Adding New Components](#adding-new-components)
    - [Changing Preferences](#changing-preferences)
      - [Changing file paths](#changing-file-paths)
      - [Changing components preferences](changing-components-preferences)

## Requirements
Please ensure your LTSpice component names are not just numbers, for example DO NOT use a component name like 123 or 245.  
Component names with just letters or both letters and numbers are expected so it is fine to use them.

<br>
<br>
<br>

## GUI guide
### Opening a schematic
---
LTSpice Schematics (.asc) can be opened using the open
a schematic a button shown in the figure below,
or using open a schematic command using the file menu.
The schematic can be of file type .asc or .txt.
Please ensure that the schematic contains
components and uses LTSpice IV or XVII.
While the schematic is being sketched a netlist file is created in the same directory as the .asc file is inside.  
The netlist feature currently only works on Windows and Linux (requires wine installed).

![Opening a schematic](https://user-images.githubusercontent.com/61741122/183928565-1fee4e97-4d83-4fb5-ac18-b40e96e601fd.gif)


#### Canvas Features
The canvas supports zoom and pan.  
To zoom just use the mouse scroll wheel,
to pan hold left click inside the schematic canvas and move your mouse.

![canvas functionality](https://user-images.githubusercontent.com/61741122/183928977-8308d5f0-643b-4338-9d54-97df3cfe9890.gif)

<br>
<br>
<br>

### Entering Parameters
---
After a schematic has been selected,
parameters if required should be entered
by clicking the enter parameters, button shown below.  
- Cancel button will just exit the enter parameters window.
- Save parameters button will make that component random, then a distrbution
  can be selected and parameters are entered.  By default if the button is
  clicked without any parameters entered the distribution will be set to Normal,
  with a mean value of 1 and a standard deviation value of 2.
- Save all parameters button assumes all constant values which were in LTSpice.
Prefixes can be entered either manually or using the dropdown list.

![Entering Component Parameters](https://user-images.githubusercontent.com/61741122/191733927-c32879a5-f511-47c4-9954-a08fca6214b5.gif)

#### Running simulations and viewing plots
After parameters are entered, simulation preferences button appears on the bottom right of the main drawing window.
The number of simulations can be specified and then the simulations are ran by clicking the button next to simulation preferences.
Two new tabs appear which are Statplots and Sobol indices.

![StatPlots Tab](https://user-images.githubusercontent.com/61741122/191734487-3e28b085-9436-436b-9bff-7507cc59029e.gif)

![Sobol Indices Tab](https://user-images.githubusercontent.com/61741122/191734509-5c2289de-881d-4021-be9b-4ee735c42890.gif)

<br>
<br>
<br>

### Opening Waveform files
---
Waveform files (.raw) can be opened using the open
a raw file button shown in the figure below or from the main window,
The raw file is then displayed as a table in the table tab.

![opening_waveform_file_smaller_size](https://user-images.githubusercontent.com/61741122/183931814-e3f39d62-d24d-4e93-bfeb-10e3fdf3a295.gif)

#### Sketching Graphs
After a Waveform file has been loaded, graphs could be sketched from the columns present in the .asc file as shown below.

![Sketching Graphs](https://user-images.githubusercontent.com/61741122/191736161-ec5a9c99-b4cb-4626-b02c-cde3a8fd69dd.gif)

<br>
<br>
<br>

### Adding New Components
---
LTSpice symbols (.asy) can be added using the add new components window.  
- Clicking the open symbol button will allow you to select a single symbol
  which can then be saved in to the symbols folder after clicking the
  save symbol button.
- Clicking load symbol will load the most recently saved symbol into the canvas
- Clicking the open folder button will allow you to select a group of symbols
  which are all then saved to Symbols folder if opened.
After a component has been opened or loaded,
right clicking inside the canvas will move the
component to the mouse position.
The Canvas also supports pan and zoom.

![Adding New Components](https://user-images.githubusercontent.com/61741122/183929535-3099217f-5830-44a3-a6f4-6fa9362d9c89.gif)

<br>
<br>
<br>

### Changing Preferences
---
#### Changing File paths
The default executable and symbol paths
can be changed in the preferences tab.  
- Additional symbol paths can be added other than the default symbol path.
- Delete file path, deletes the selected file path from the
  additional symbol paths.
- Default deletes all added file paths and returns the default executable
  and symbol paths.

![changing_file_preferences](https://user-images.githubusercontent.com/61741122/183949890-aeb7a1de-2933-481f-b1cb-2cb6bfca7129.gif)

<br>
<br>

#### Changing components preferences
The components drawn on the canvas can be customised according
to the preferences set
Select Edit and the Preferences and then click change component preferences
The outline colour, fill colour and outline width can be changed as shown below

![changing_drawing_preferences](https://user-images.githubusercontent.com/61741122/183930232-e7747f2f-66fb-476f-b612-ac176fec8535.gif)




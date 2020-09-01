<h1>Overview</h1>
This program is a discrete event simulation that was written with the primary focus of modeling continuous industrial chemical processes. The program is general and can be modified to fit a wide variety of processes by scripting custom modules for use 
in the simulation. Modules can then be dynamically added to and configured within the simulation to match the system that is 
being proposed or exists in the real world. A few example use cases for this simulation are sizing proposed industrial 
systems and using readily available information from an existing system to determine information that would be otherwise 
difficult to obtain. 

The example shown in the demonstration below is that of a hydrocyclone system that is typical in pulp and paper mills. These systems are used to remove dirt, metal, and other debris from a pulp slurry in the papermaking process. 
<h1>Demonstration</h1>
This animation demonstrates how to create a single stage hydrocyclone system. The "source" module represents an upstream process which is outputting a certain amount of flow to the pump.The "tank" module is used to supply the difference in flow that exists between what the "source" module pushes forward and what the pump pulls. These two types of flow, push and pull, are represented by square and circle sockets, respectively. 

<img src="https://github.com/herstky/DES/raw/master/demos/model_creation.gif" height="350" width="663">
<img src="https://github.com/herstky/DES/raw/master/demos/changing_settings.gif" height="350" width="663">
<img src="https://github.com/herstky/DES/raw/master/demos/hydrocyclone_cascade.gif" height="350" width="663">


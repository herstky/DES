<h1>Overview</h1>
This program is a discrete event simulation that was written with the primary focus of modeling continuous industrial chemical processes. The program is general and can be modified to fit a wide variety of processes by scripting custom modules for use 
in the simulation. Modules can then be dynamically added to and configured within the simulation to match a system that is 
being proposed to a client or exists in the real world. Example use cases for this simulation include, but are not limited to, sizing proposed industrial systems and using readily available information from an existing system to determine process parameters that would be otherwise difficult to obtain. 

The examples shown in the demonstration below feature a couple different configurations of hydrocyclone systems that are typical in pulp and paper mills. These systems are used in the papermaking process to remove dirt, metal, and other debris from a wood pulp slurry. 
<h1>Demonstration</h1>
<br>
<figure>
    <img src="https://github.com/herstky/DES/raw/master/demos/model_creation.gif" height="528" width="1000">
</figure>
This animation demonstrates how to create a single-stage hydrocyclone system. The "source" module represents an upstream process which is outputting a certain amount of flow to the pump. The "tank" module is used to supply the difference in flow that exists between what the "source" module pushes forward and what the pump pulls. These two types of flow, push and pull, are represented by square and circle sockets, respectively. The numbers shown in the readouts are, in the order they appear, volumetric flowrate in cubic meters per minute, consistency (percent solids), and metric tons of solids produced per day. 
<br>
<br>
<br>
<br>
<br>
<figure>
    <img src="https://github.com/herstky/DES/raw/master/demos/changing_settings.gif" height="528" width="1000">
</figure>
Module settings can be adjusted while the simulation is running to fine tune process variables.
<br>
<br>
<br>
<br>
<br>
<figure>
    <img src="https://github.com/herstky/DES/raw/master/demos/hydrocyclone_cascade.gif" height="528" width="1000">
</figure>
This is a 3-stage hydrocyclone cascade. Multistage systems such as this are used to reclaim some good fiber that would otherwise be rejected to the sewer. The simulation takes a moment to reach steady state for more complicated systems.


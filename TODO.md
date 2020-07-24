Refactor Module capacities
Refactor Module event transfers to methods
Pull flow
Support arbitrary number of components: water, fiber, filler, etc.
-> Should be as simple as adding a Component class that has component name and magnitude as attributes
-> Add components list to Event class
-> Each instance of Event may need to have the same list of components, but with different values for magnitudes
GUI 
More blocks
-> Implementing a GUI first will simplify the process of setting up streams

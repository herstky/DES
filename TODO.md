Refactor Module capacities
Refactor Module event transfers to methods
Refactor Component class into species dictionaries
- Each event object should have a separate member for each solids, liquids, and gases 
Pull flow
Support arbitrary number of components: water, fiber, filler, etc.
- Should be as simple as adding a Component class that has component name and magnitude as attributes
- Add components list to Event class
- Each instance of Event may need to have the same list of components, but with different values for magnitudes
More blocks
Comments

Considerations:
- Refactor Multiline class into helper functions
- Remove floating_line member from gui
    - set fragmented lines as chains of parent->child QGraphicsItems
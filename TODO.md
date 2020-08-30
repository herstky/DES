Verify Module capacity correctness
Comments
Save and load
Refactor creating, drawing, and completion of streams and readouts
- Should only have one floating object
Investigate flow imbalances due to rounding errors when distributing flow to connections 
when the number of events in a module doesn't divide evenly among the number of outlets.

Considerations:
- Remove floating_line member from gui
    - Set fragmented lines as chains of parent->child QGraphicsItems
- Change event.volume member to magnitude to be more general
- Rename Connection to Socket
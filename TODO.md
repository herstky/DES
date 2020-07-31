Refactor Module capacities
Refactor Module event transfers to methods
Pull flow
More blocks
Comments
Save and load
Start stream by clicking any connection without a stream
Refactor creating, drawing, and completion of streams and readouts
- Should only have one floating object
Event system should be fully encapsulated
Source modules should add events to own queue then transfer out?

Considerations:
- Refactor Multiline class into helper functions
- Remove floating_line member from gui
    - Set fragmented lines as chains of parent->child QGraphicsItems
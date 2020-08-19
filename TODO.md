Verify Module capacity correctness
Bugtest creating/placing streams and readouts
Cancel module/stream/readout placement
More modules
Comments
Save and load
Start stream by clicking any connection without a stream
Refactor creating, drawing, and completion of streams and readouts
- Should only have one floating object
Event system should be fully encapsulated
- Abstract event generation and destruction away from Modules
    - source transfers a volume to its outlet connection, outlet connection generates new events

Considerations:
- Refactor Multiline class into helper functions
- Remove floating_line member from gui
    - Set fragmented lines as chains of parent->child QGraphicsItems
- Change event.volume member to magnitude to be more general
- Convert some or all Module views to widgets
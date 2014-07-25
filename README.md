StateChange
============

Maintains a *state* and when *state* changes, a signal is notified that containes the *state* and *prev_state*.

Persistence is used to maintain the *state*.

Properies
---------

-   **state_expr**: Expression property that evalues to *state*. If the expression cannot be evaluated, the *state* will not change.
-   **backup_interval** (seconds=600): Inteval at which *state* is saved to disk.

Dependencies
------------
None

Commands
--------
None

Input
-----
Any list of signals. Each signal will be evaluated against **state_expr** to determine the new *state* of the block.

Output
------
When *state* changes, a signal is notifed with attribues *state* and *prev_state*. No signal is emitted when the *prev_state* is None. This is to prevent a notification when initialzing the *state*.

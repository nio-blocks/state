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

------------------

Relay
============

Maintains a *state*

- When *state* is True, signals can pass through
- When *state* is False, signals are blocked

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
Any list of signals Signals will be passed through if bool(*state*) == True, else they will be blocked

Output
------
When *state* is True, all signals are output

When *state* is False, no signals are output

-------------

MergeState
============

Maintains a *state* and merges that state (with name **state_name**) with every signal that passes through

Properies
---------

-   **state_expr**: Expression property that evalues to *state*. If the expression cannot be evaluated, the *state* will not change.
-   **state_name**: String property that is the name of the appended *state*
-   **backup_interval** (seconds=600): Inteval at which *state* is saved to disk.

Dependencies
------------
None

Commands
--------
None

Input
-----
Any list of signals. Signals that evaluate through **state_expr** to change *state* will do so.

**All** signals will be passed through with *state* appended to them (including signals that are evaluated)

Output
------
Every signal is passed through with **state_name**: *state* merged on.

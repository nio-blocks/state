State Blocks
============

This repository contains blocks that can maintain a state.
 * [StateChange](#statechange)
 * [Relay](#relay)
 * [MergeState](#mergestate)


Many of the blocks share the same configuration properties and behavior though.

Persistence is used to maintain the *state*. If use_persistence is enabled, that value will populate the initial state and _not_ the initial state configuration value. Any new states (from new groups) will use the configured initial state for their initial state though

Properties
---------

-   **state_expr**: (expression) Property that evalues to *state*. If the expression cannot be evaluated, the *state* will not change.
-   **initial_state**: (expression) What the initial state should be
-   **use_persistence**: (bool) Whether to load the initial state from persistence
-   **group_by**: (expression) What to group the signals by. A different state will be maintained for each group
-   **backup_interval** (seconds=600): Inteval at which *state* is saved to disk.

Dependencies
------------
None

Commands
--------
-   **current_state** (parameter: group): Gets the current state for a given group. Response is a dictionary with "state" and "group" keys. If 'group' is not specified then a list is returned with a dictionary for each group. If the specified group does not exist, then an empty dicitonary is returned.

Input
-----

### default

Any list of signals. Each signal will be evaluated against **state_expr** to determine the new *state* of the block for the signal's group.

### setter

Signals passed to this input will always (and only) be used to set the state. They ignore **sate_sig**.

Output
------
Depends on the individual block


------------------


StateChange
============

Maintains a *state* and when *state* changes, a signal is notified that containes the *state* and *prev_state*.


Additional Properties
---------

-   **exclude**: Select whether you want to exclude other signals. If checked, the only output will be *state* and *prev_state*. If not checked, *state* and *prev_state* will be appended onto the incomming signal.


Output
------
When *state* changes, a signal is notifed with attribues *state*, *prev_state*, and *group*. If exclude is _unchecked_ then the signal that changed the state will have the attributes added to it.

------------------


Relay
============

If *state_sig* evaluates to True, then it is used to set the *state*. Else, the signal is notified if *state* is True.

- When *state* is True, signals can pass through
- When *state* is False, signals are blocked

Additional Properties
---------

-   **state_sig**: If True, signal is used to set *state*. Else, the signal is notified if *state* is True.


Output
------
When *state* is True, non state-setting signals are output

When *state* is False, no signals are output

-------------

MergeState
============

Maintains a *state* and merges that state (with name **state_name**) with signals that passes through

Additional Properties
---------

-   **state_sig**: If True, signal is used to set *state*. Else, the signal is notified and *state* is assigned to the attribute *state_name*.
-   **state_name**: String property that is the name of the appended *state*

Output
------
Non state setting signals are passed through with *state* set to the attribue **state_name**.

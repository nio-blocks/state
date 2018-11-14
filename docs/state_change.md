StateChange
===========
For every signal processed a **State** is evaluated using [nio expressions](https://docs.n.io/blocks/expressions.html) and its value stored internally. If **State** evaluates to a value different from the previous evaluation for that `group` a signal is emitted which contains the current and previous **State**. The current **State** can optionally be loaded from disk when the block starts, otherwise the first signal processed will be compared to the **Initial State**.

Properties
----------
- **State**: This evaluation sets the current state.
- **Initial State**: Evaluation to use for the current state (all groups) when the block starts, before any signals have been processed. Superseded by values loaded from persistence, if applicable.
- **Group By**: Expression which defines a signal's `group`, a **State** is maintained for every unique group processed.
- **Exclude Existing Fields**: If checked (True) incoming signals will be discarded, and outoging signals will contain only the results of the **State** evaluation.

Advanced Properties
-------------------
- **Load From Persistence**: The block's current **State** will be saved to disk when stopped, and if checked (True) that **State** will replace the **Initial State** when the block is started. Please see [docs/data/persistence](https://docs.n.io/data/persistence.html) for more information.
- **State Name**: Attribute of the outgoing signal in which to store the current **State**, defaults to `state`.

Examples
--------
States can be used to process a stream of data into discrete events, for example when a process value is out of spec:

```
State: {{ $temp_C > 0 }}
Exclude Existing Fields: False
```
<table width=100%>
<tr>
<th>Incoming Signals</th>
<th>Outgoing Signals</th>
</tr>
<tr>
<td>
<pre>
[
  {"temp_C": -2.0}
]
</pre>
</td>
<td>
<pre>
[
  {"group": None, "state": False, "prev_state": None, "temp_C: -2.0}
]
</pre>
</td>
</tr>
<tr>
<td>
<pre>
[
  {"temp_C": -1.0}
]
</pre>
</td>
<td>
<br>
<em>none, the current state is unchanged because the result of -1.0 > 0 is False</em>
</td>
</tr>
<tr>
<td>
<pre>
[
  {"temp_C": 1.0}
]
</pre>
</td>
<td>
<pre>
[
  {"group": None, "state": True, "prev_state": False, "temp_C: 1.0}
]
</pre>
</td>
</tr>
</table>

By setting the **Group By** property multiple similar streams can be processed by the same block. In addition, setting an **Initial State** can prevent a "change" of state when a new group is processed for the first time. In this example, each *freezer* is processed for the first time and its current **State** is compared to the defined **Initial State**, and a signal notified only if there is a new **State**. In that case the **Initial State** will be used for the value of `prev_state` in the outgoing signal:

```
Group By: {{ $freezer }}
State: {{ $temp_C > 0 }}
Initial State: {{ False }}
State Name: out_of_spec
Exclude Existing Fields: True
```
<table width=100%>
<tr>
<th>Incoming Signals</th>
<th>Outgoing Signals</th>
</tr>
<tr>
<td>
<pre>
[
  {"freezer": 1, "temp_C": 1.0},
  {"freezer": 2, "temp_C": -2.0},
  {"freezer": 3, "temp_C": -3.0}
]
</pre>
</td>
<td>
<pre>
[
  {"group": 1, "out_of_spec": True, "prev_state": False}
]
</pre>
</td>
</tr>
</table>

Commands
--------
- **current_state**: Get the current **State** of a *group*
  - *group*: If `None` this command returns all groups
- **groups**: Get a list of all groups

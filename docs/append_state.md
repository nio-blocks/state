AppendState
===========
This block has two inputs, the `setter` behaves like and is configured exactly like a [StateChange](state_change.md) block, and its current **State** is appened to every signal processed by the `getter` input. That is to say, the `setter` *sets* a **State**, and the `getter` *gets* the current **State** for the same `group`.

See Also: [MergeStreams](https://blocks.n.io/MergeStreams)

Properties
----------
- **State**: This evaluation sets the current state from the `getter` input.
- **Initial State**: Evaluation to use for the current state (all groups) when the block starts, before any signals have been processed by the `setter`. Superseded by values loaded from persistence, if applicable.
- **State Name**: Attribute of the outgoing signal in which to store the current **State**, defaults to `state`.
- **Group By**: Expression which defines a signal's `group`, a **State** is maintained for every unique group processed, and signals processed at the `getter` input will be appended with the current **State** for that `group`.

Advanced Properties
-------------------
- **Load From Persistence**: The block's current **State** will be saved to disk when stopped, and if checked (True) that **State** will replace the **Initial State** when the block is started. Please see [docs/data/persistence](https://docs.n.io/data/persistence.html) for more information.

Examples
--------
In this example, the last value from one stream is added to signals from another stream:
```
State: {{ $numbers }}
```
<table width=100%>
<tr valign="top">
<th align="left">Incoming Signals, Getter</th>
<th align="left">Incoming Signals, Setter</th>
<th align="left">Outgoing Signals</th>
</tr>

<tr valign="top">
<td>

*none*
</td>
<td>
<pre>
[
  {
    "numbers": 0
  }
]
</pre>
</td>
<td>

*none*
</td>
</tr>

<tr valign="top">
<td>
<pre>
[
  {
    "letters": "A"
  }
]
</pre>
</td>
<td>

*none*
</td>
<td>
<pre>
[
  {
    "letters": "A",
    "state": 0
  }
]
</pre>
</td>
</tr>

<tr valign="top">
<td>
<pre>
[
  {
    "letters": "B"
  }
]
</pre>
</td>
<td>

*none*
</td>
<td>
<pre>
[
  {
    "letters": "B",
    "state": 0
  }
]
</pre>
</td>
</tr>

<tr valign="top">
<td>

*none*
</td>
<td>
<pre>
[
  {
    "numbers": 1
  }
]
</pre>
</td>
<td>

*none*
</td>
</tr>

<tr valign="top">
<td>
<pre>
[
  {
    "letters": "C"
  }
]
</pre>
</td>
<td>

*none*
</td>
<td>
<pre>
[
  {
    "letters": "C",
    "state": 1
  }
]
</pre>
</td>
</tr>
</table>

If, for example, we want to get a current temperature value from a freezer every time the door opens or closes, we can use **Group By** to match up streams from doors and temps:

```
Group By: {{ $freezer }}
State: {{ $temp_C }}
State Name: temp_C
```
<table width=100%>
<tr valign="top">
<th align="left">Incoming Signals, Getter</th>
<th align="left">Incoming Signals, Setter</th>
<th align="left">Outgoing Signals</th>
</tr>

<tr valign="top">
<td>

*none*
</td>
<td>
<pre>
[
  {
    "freezer": 1,
    "temp_C": -1.0
  },
  {
    "freezer": 2,
    "temp_C": -2.0
  },
  {
    "freezer": 3,
    "temp_C": -3.0
  }
]
</pre>
</td>
<td>

*none*
</td>
</tr>

<tr valign="top">
<td>
<pre>
[
  {
    "freezer": 1,
    "door_open": True
  }
]
</pre>
</td>
<td>

*none*
</td>
<td>
<pre>
[
  {
    "freezer": 1,
    "door_open": True,
    "temp_C": -1.0
  }
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

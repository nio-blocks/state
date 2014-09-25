from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock

class StateChangeVolatile(Block):
    """ Notifies a signal on *state* change.

    Maintains a *state*. When *state* changes, a signal is notified
    that containes the *state* and *prev_state*.

    *state* is set by the *state_expr* property. It is an expression
    property that evalues to *state*. If the expression fails,
    then the *state* remains unmodified.

    *state* changing from None to not None does not count as a state change.
    This makes is so that setting the initial state does not trigger
    a notification Signal.
    """
    state_expr = ExpressionProperty(title='State Expression', attr_default=NameError)
    backup_interval = TimeDeltaProperty(title='Backup Interval',
                                        default={'seconds': 600})

    def __init__(self):
        super().__init__()
        self._state = None
        self._backup_job = None
        self._lock = Lock()

    def configure(self, context):
        super().configure(context)
        self._state = self.persistence.load('state') or self._state

    def start(self):
        super().start()
        self._backup_job = Job(
            self._backup,
            self.backup_interval,
            True
        )

    def stop(self):
        self._backup_job.cancel()
        self._backup()

    def process_signals(self, signals):
        for signal in signals:
            out = self._process_state(signal)
            if out is not None:
                self.notify_signals(out)

    def _process_state(self, signal):
        with self._lock:
            prev_state = self._state
            try:
                state = self.state_expr(signal)
                if state is not NameError:
                    self._state = state
                else:
                    print("Got Default!")
                    return
            except Exception as e:
                self._state_change_error(e)
                return
            if prev_state is not None and self._state != prev_state:
                # notify signal if there was a prev_state and
                # the state has changed.
                signal = Signal({
                    "state": self._state,
                    "prev_state": prev_state
                })
                return [signal]

    def _backup(self):
        ''' Persist the current state using the persistence module.

        '''
        self.persistence.store(
            "state",
            self._state
        )
        self.persistence.save()

    def _state_change_error(self, e):
        self._logger.error("State Change failed: {}".format(str(e)))


@Discoverable(DiscoverableType.block)
class StateChange(StateChangeVolatile):
    def __init__(self):
        super().__init__()
        self._safe_lock = Lock()

    def process_signals(self, signals):
        with self._safe_lock:
            for signal in signals:
                out = self._process_state(signal)
                if out is not None:
                    self.notify_signals(out)



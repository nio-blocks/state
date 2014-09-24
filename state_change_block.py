from nio.common.block.base import Block
from nio.common.discovery import Discoverable, DiscoverableType
from nio.common.signal.base import Signal
from nio.metadata.properties.expression import ExpressionProperty
from nio.metadata.properties.timedelta import TimeDeltaProperty
from nio.modules.scheduler import Job
from nio.modules.threading import Lock


@Discoverable(DiscoverableType.block)
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
    state_expr = ExpressionProperty(title='State Expression')
    backup_interval = TimeDeltaProperty(title='Backup Interval',
                                        default={'seconds': 600})

    def __init__(self):
        super().__init__()
        self._state = None
        self._prev_state = None
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
            with self._lock:
                try:
                    prev_state = self._state
                    self._state = self.state_expr(signal)
                    state = self._state
                except Exception as e:
                    self._logger.error("State Change failed: {}".format(str(e)))
                    continue
                if prev_state is not None and state != prev_state:
                    # notify signal if there was a prev_state and
                    # the state has changed.
                    signal = Signal({
                        "state": state,
                        "prev_state": prev_state
                    })
                    self.notify_signals([signal])

    def _backup(self):
        ''' Persist the current state using the persistence module.

        '''
        self.persistence.store(
            "state",
            self._state
        )
        self.persistence.save()
        
 
 class StateChange(StateChangeVolatile):
     def process_signals(self, signals):
        with self._lock:
            state = self._state
            for signal in signals:
                prev_state = state
                try:
                    state = self.state_expr(signal)
                except:
                    self._logger.error("State Change failed: {}".format(str(e)))
                    continue
                if prev_state is not None and state != prev_state:
                    # notify signal if there was a prev_state and
                    # the state has changed.
                    signal = Signal({
                        "state": state,
                        "prev_state": prev_state
                    })
                    self.notify_signals([signal])
            self._state = state

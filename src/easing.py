import math
from time import perf_counter


class Easing:

    __slots__ = ('time_based', 'last_call', 'decay', 'starting_value', '_current', 'ignored', '_target',
                 'multiplier', 'offset', 'constrain_to_pixels', 'queued_movement')

    def __init__(self, initial_val, target_val=None, decay=0.2, constrain_to_pixels=True):
        self.time_based = True
        self.last_call = 0
        self.decay = decay
        self.starting_value = initial_val
        self.ignored = 0
        self.offset = 0
        self._current = initial_val
        self._target = float(initial_val) if target_val is None else float(target_val)
        self.constrain_to_pixels = constrain_to_pixels
        self.multiplier = 1
        self.queued_movement = 0

    def __call__(self):
        return self.current

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, value):
        self._target = value

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        self._current = value

    @property
    def is_animating(self):
        diff = self._current - self._target
        is_animating = diff * diff > 0.05
        if not is_animating:
            self._current = self._target

        return is_animating

    @property
    def abs_delta(self):
        return abs(self._target - self._current)

    @property
    def delta(self):
        return self._target - self._current

    def get(self):
        return self._current + self.offset

    def snap_to_target(self, offset=0):
        if offset == 0:
            self._current = self._target
        else:
            t = self._target - offset if self._target > self._current else self._target + offset
            self._current = t

    def reset(self):
        self._target = self.starting_value

    def mul(self, value):
        self._target *= value

    def set(self, target, limit=-1, instant=False, preserve_slew=True):
        if instant or 0 <= limit < abs(target - self._target):
            current_slew = self._target - self._current
            self._current = target
            if preserve_slew:
                self._current -= current_slew

        self._target = target

    def move(self, amount, instant=False, preserve_slew=True):
        current_slew = self._target - self._current
        self._target += amount
        if instant:
            self._current = self._target
            if preserve_slew:
                self._current -= current_slew

    def shift(self, amount):
        self._current += amount

    def exp_decay(self, dt):
        """time based exponential decay easing function"""
        adjusted_decay = self.decay * 80
        return self._target + (self._current - self._target) * math.exp(-adjusted_decay * dt)

    def _time_based_easing_update(self):
        previous_call = self.last_call
        self.last_call = (curr_time := perf_counter())
        if self.is_animating:
            delta = self._target - self._current
            threshold = 0.3
            if abs(delta) < threshold:
                self._current = self._target
            else:
                self._current = self.exp_decay(curr_time - previous_call)

    def _easing_update(self):
        if self.is_animating:
            decay_factor = self.decay * self.multiplier
            self._current = self._current + (self._target - self._current) * decay_factor
        else:
            self._current = self._target

    def update(self):
        if self.time_based:
            self._time_based_easing_update()
        else:
            self._easing_update()

        if self.constrain_to_pixels:
            return round(self._current + self.offset)
        else:
            return self._current + self.offset


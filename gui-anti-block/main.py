import sys
from typing import Optional
from datetime import datetime

import pyautogui

from time import sleep


# Avoid interruption when mouse is in the corner
pyautogui.FAILSAFE = False


class MouseWatcher:
    # Seconds
    tick_interval = 1 * 60
    move_interval = 5 * 60
    idle_interval = 15 * 60

    last_tick: Optional[datetime] = None
    last_pos: Optional[pyautogui.Point] = None

    curr_tick: Optional[datetime] = None
    curr_pos: Optional[pyautogui.Point] = None

    active_begin: Optional[datetime] = None
    active_end: Optional[datetime] = None
    active_hours: float = 0

    active_days = './active_days.txt'
    active_blocks = './active_blocks.txt'

    last_move: Optional[datetime] = None
    last_active: Optional[datetime] = None

    def tick(self):
        self.curr_tick = datetime.now()
        self.curr_pos = pyautogui.position()

        if self.last_pos != self.curr_pos:
            if not self.active_begin:
                self.active_begin = self.curr_tick
                print(f'Activity starts at {self.active_begin}')

            self.active_end = self.curr_tick
            self.last_move = self.curr_tick
            print(f'Activity continues at {self.active_end}')

        if self.check_interval(self.last_active, self.curr_tick, self.idle_interval):
            self.active_flush()
            self.last_active = self.curr_tick

        if self.check_interval(self.last_move, self.curr_tick, self.move_interval):
            pyautogui.moveRel(+1, +1)
            pyautogui.moveRel(-1, -1)
            self.last_move = self.curr_tick
            print(f'Signal sent at {self.last_move}')

        self.last_tick = self.curr_tick
        self.last_pos = self.curr_pos

        sleep(self.tick_interval)

    def check_interval(self, last: Optional[datetime], curr: Optional[datetime], interval: float):
        return not last or not curr or (curr - last).total_seconds() > interval

    def active_flush(self):
        if (self.active_begin
                and self.active_end
                and self.curr_tick
                and self.check_interval(self.active_end, self.curr_tick, self.idle_interval)):
            block_hours = (self.active_end - self.active_begin).total_seconds() / 3600

            if block_hours > 0:
                self.active_hours = self.active_hours + block_hours

                with open(self.active_blocks, mode='a') as f:
                    f.write(f'{self.active_begin}\t{block_hours}\n')

                if self.active_begin.date() != self.curr_tick.date():
                    with open(self.active_days, mode='a') as f:
                        f.write(f'{self.active_begin}\t{self.active_hours}\n')

                print(f'Activity flushed at {self.last_active}')

            self.active_begin = None
            self.active_end = None


if __name__ == '__main__':
    watcher = MouseWatcher()

    try:
        while True:
            watcher.tick()
    except KeyboardInterrupt:
        print('\nStopping...')
    except Exception as e:
        print(e, file=sys.stderr)

    watcher.active_flush()

    print('Bye!')
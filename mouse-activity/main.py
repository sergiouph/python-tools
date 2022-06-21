import typing
import json
import sys
import datetime
import pyautogui
import time
import os

# Avoid interruption when mouse is in the corner
pyautogui.FAILSAFE = False


DB_NAME = './mouse-activity.json'

# Seconds
tick_interval = 1 * 60
move_interval = 5 * 60
idle_interval = 15 * 60
show_interval = 20 * 60

ISO_WEEKDAYS = {
    1: 'MON',
    2: 'TUE',
    3: 'WED',
    4: 'THU',
    5: 'FRI',
    6: 'SAT',
    7: 'SUN',
}


class State:
    last_tick: typing.Optional[datetime.datetime] = None
    last_pos: typing.Optional[pyautogui.Point] = None

    curr_tick: typing.Optional[datetime.datetime] = None
    curr_pos: typing.Optional[pyautogui.Point] = None

    active_begin: typing.Optional[datetime.datetime] = None
    active_end: typing.Optional[datetime.datetime] = None

    last_move: typing.Optional[datetime.datetime] = None
    last_show: typing.Optional[datetime.datetime] = None


def load_data() -> typing.Dict[str, str]:
    if not os.path.exists(DB_NAME):
        return {}

    with open(DB_NAME, mode='r') as fp:
        return json.load(fp)


def save_data(data: typing.Dict[str, str]):
    with open(DB_NAME, mode='w') as fp:
        return json.dump(data, fp)


def update_block(
        begin: datetime.datetime,
        end: datetime.datetime,
):
    data = load_data()

    data[begin.isoformat()] = end.isoformat()

    save_data(data)


def check_interval(
        last: typing.Optional[datetime.datetime],
        curr: typing.Optional[datetime.datetime],
        interval: float,
):
    return last and curr and (curr - last).total_seconds() > interval


def generate_report():
    now = datetime.date.today()
    begin_date = (now - datetime.timedelta(now.isoweekday() + 7))

    week_days: typing.Dict[str, typing.Dict[str, float]] = {}
    data = load_data()

    for begin, end in data.items():
        begin_dt = datetime.datetime.fromisoformat(begin)
        begin_dt.toordinal()
        if begin_dt.date() > begin_date:
            week_id = begin_dt.strftime('%U')
            end_dt = datetime.datetime.fromisoformat(end)

            date = begin_dt.date().isoformat()
            hours = (end_dt - begin_dt).total_seconds() / 3600.0

            day_hours = week_days.get(week_id, {})
            day_hours[date] = hours + day_hours.get(date, 0)
            week_days[week_id] = day_hours

    output: typing.List[str] = []

    for week, day_hours in week_days.items():
        week_hours = 0

        output.append(f'---------------- #{week}\n')

        for date, hours in day_hours.items():
            output.append(date)
            output.append(' ')
            output.append(ISO_WEEKDAYS.get(datetime.date.fromisoformat(date).isoweekday(), '?'))
            output.append(' ')
            output.append(format_hours(hours))
            output.append('\n')

            week_hours += hours

        output.append(f'  Week Hours -> {format_hours(week_hours)}\n')

    output.append('----------------')

    return ''.join(output)


def format_hours(value: float) -> str:
    h = int(value)
    m = int(60 * (value - h))

    return f'{h}:{"%02i" % m}'


def tick(state: State):
    state.curr_tick = datetime.datetime.now()
    state.curr_pos = pyautogui.position()

    # Update activity block
    if state.last_pos != state.curr_pos:
        if not state.active_begin:
            state.active_begin = state.curr_tick
            print(f'Activity starts at {state.active_begin}')

        state.active_end = state.curr_tick
        state.last_move = state.curr_tick

        update_block(state.active_begin, state.active_end)

        print(f'Activity continues at {state.active_end}')

    # Clear activity block after idle interval
    if check_interval(state.active_end, state.curr_tick, idle_interval):
        state.active_begin = None
        state.active_end = None
        print(f'Activity reset at {state.curr_tick}')

    # Send activity signal if required
    if check_interval(state.last_move, state.curr_tick, move_interval):
        pyautogui.moveRel(+1, +1)
        pyautogui.moveRel(-1, -1)
        state.last_move = state.curr_tick
        print(f'Activity signal sent at {state.last_move}')

    if not state.last_show or check_interval(state.last_show, state.curr_tick, show_interval):
        print(generate_report())
        state.last_show = state.curr_tick

    state.last_tick = state.curr_tick
    state.last_pos = state.curr_pos

    time.sleep(tick_interval)


def main():
    state = State()

    try:
        while True:
            tick(state)
    except KeyboardInterrupt:
        print('\nStopping...')
    except Exception as e:
        print(e, file=sys.stderr)

    print('Bye!')


if __name__ == '__main__':
    main()

from typing import Callable, Literal, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

def status_type(name: str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        setattr(func, "_status_type", name)
        return func
    return decorator

@status_type("percentage")
def percentage(perc_min: int, perc_max: int, value: int) -> int:
    if perc_max < perc_min:
        result = (perc_min - value) * 100 // (perc_min - perc_max)
    else:
        result = (value - perc_min) * 100 // (perc_max - perc_min)
    return max(0, min(100, result))

@status_type("on_off")
def on_off(value: int, on: int, off: int) -> Literal['on', 'off']:
    return 'on' if value == on else 'off'

@status_type("int_str_mapping")
def int_str_mapping(values: dict[int, str], value: int) -> str|None:
    return values.get(value, None)

@status_type("int_int_mapping")
def int_int_mapping(values: dict[int, int], value: int) -> int|None:
    return values.get(value, None)

@status_type("two_sided_chatmix")
def two_sided_chatmix(active_min: int, active_max: int, value: int) -> int:
    """For Arctis 7-style chatmix: value=0 means opposite side active (this channel at 100%).
    Otherwise maps active_min→0% to active_max→100%."""
    if value == 0:
        return 100
    return max(0, min(100, (value - active_min) * 100 // (active_max - active_min)))

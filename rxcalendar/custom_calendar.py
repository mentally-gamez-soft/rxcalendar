"""Custom calendar component built with pure Reflex components."""

from datetime import datetime, timedelta
from calendar import monthrange
import reflex as rx
from typing import Callable


def get_month_data(year: int, month: int) -> list[list[dict]]:
    """Get calendar data for a month organized by weeks.
    
    Returns a list of weeks, where each week is a list of day dictionaries.
    Each day dict contains: day number, is_current_month, date_str, is_weekday
    """
    # Get first day of month and number of days
    first_day_weekday, num_days = monthrange(year, month)
    
    # Create list to hold weeks
    weeks = []
    current_week = []
    
    # Add empty cells for days before month starts
    # Monday is 0, Sunday is 6 in calendar module
    for _ in range(first_day_weekday):
        current_week.append({
            "day": 0,
            "is_current_month": False,
            "date_str": "",
            "is_weekday": False
        })
    
    # Add all days of the month
    for day in range(1, num_days + 1):
        date = datetime(year, month, day)
        date_str = date.strftime("%a %b %d %Y")
        weekday = date.weekday()  # 0 = Monday, 6 = Sunday
        is_weekday = weekday < 5  # Monday-Friday
        
        current_week.append({
            "day": day,
            "is_current_month": True,
            "date_str": date_str,
            "date_iso": date.strftime("%Y-%m-%d"),
            "is_weekday": is_weekday
        })
        
        # If week is complete (7 days) or it's the last day, add to weeks
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    
    # Fill remaining days in last week
    if current_week:
        while len(current_week) < 7:
            current_week.append({
                "day": 0,
                "is_current_month": False,
                "date_str": "",
                "is_weekday": False
            })
        weeks.append(current_week)
    
    return weeks


def calendar_day_cell_func(day_data: dict, on_click_handler: Callable, state_ref) -> rx.Component:
    """Create a single day cell in the calendar."""
    if not day_data["is_current_month"]:
        # Empty cell for days outside current month
        return rx.box(
            width="100%",
            height="50px",
            background="var(--gray-2)",
        )
    
    date_iso = day_data.get("date_iso", "")
    
    # Style based on whether it's a weekday or weekend
    base_style = {
        "width": "100%",
        "height": "50px",
        "border_radius": "4px",
        "font_weight": "500",
        "position": "relative",
        "display": "flex",
        "flex_direction": "column",
        "align_items": "center",
        "justify_content": "center",
    }
    
    if day_data["is_weekday"]:
        # Weekday - clickable. Use state to get flag color
        flag_color = state_ref.flag_colors_by_date.get(date_iso, "var(--accent-2)")
        hours_val = state_ref.hours.get(date_iso, 0.0)
        
        return rx.box(
            # Day number
            rx.text(str(day_data["day"]), size="3", weight="medium"),
            # Hours (if > 0 and no flag)
            rx.cond(
                hours_val > 0.0,
                rx.text(f"{hours_val}h", size="1", color="var(--gray-11)"),
                rx.box(),
            ),
            # Range start indicator
            rx.cond(
                state_ref.range_start_date == date_iso,
                rx.badge("START", size="1", color_scheme="blue", position="absolute", top="2px", right="2px"),
                rx.box(),
            ),
            on_click=lambda: on_click_handler(day_data["date_str"]),
            on_mouse_enter=lambda: state_ref.set_hovered_date(day_data["date_str"]),
            on_mouse_leave=lambda: state_ref.set_hovered_date(""),
            cursor="pointer",
            background=flag_color,
            border=rx.cond(
                state_ref.range_start_date == date_iso,
                "2px solid var(--accent-9)",
                "1px solid var(--gray-6)"
            ),
            _hover={
                "transform": "scale(1.05)",
                "box_shadow": "0 2px 8px rgba(0,0,0,0.15)",
            },
            transition="all 0.15s",
            **base_style
        )
    else:
        # Weekend - not clickable
        return rx.box(
            rx.text(str(day_data["day"])),
            background="var(--gray-3)",
            color="var(--gray-9)",
            cursor="not-allowed",
            border="1px solid var(--gray-6)",
            **base_style
        )


def custom_month_calendar(year: int, month: int, on_click_day: Callable, state_ref=None) -> rx.Component:
    """Create a custom calendar for a specific month."""
    from .state import CalendarState
    if state_ref is None:
        state_ref = CalendarState
    
    weeks = get_month_data(year, month)
    
    # Day headers
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    return rx.box(
        # Day name headers
        rx.grid(
            *[
                rx.box(
                    rx.text(
                        day_name,
                        size="2",
                        weight="bold",
                        color="var(--gray-11)",
                    ),
                    text_align="center",
                    padding="4px",
                )
                for day_name in day_names
            ],
            columns="7",
            spacing="1",
            margin_bottom="4px",
        ),
        # Calendar grid
        rx.box(
            *[
                rx.grid(
                    *[calendar_day_cell_func(day, on_click_day, state_ref) for day in week],
                    columns="7",
                    spacing="1",
                    margin_bottom="2px",
                )
                for week in weeks
            ],
        ),
        width="100%",
        padding="8px",
    )

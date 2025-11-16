"""UI components for the calendar application."""

from datetime import datetime
import reflex as rx
from .state import CalendarState
from .custom_calendar import custom_month_calendar


def month_calendar(month: int, year: int = 2026) -> rx.Component:
    """Create a calendar component for a specific month."""
    # Create a date string for the first day of the month
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    return rx.vstack(
        rx.hstack(
            rx.heading(
                month_names[month - 1],
                size="5",
            ),
            rx.spacer(),
            # Bulk hours button (only visible for managers and HR)
            rx.cond(
                CalendarState.current_user_role != "employee",
                rx.button(
                    rx.icon("clock", size=14),
                    "Set Hours",
                    on_click=lambda: CalendarState.open_bulk_hours_dialog(month),
                    size="1",
                    variant="soft",
                    color_scheme="blue",
                ),
                rx.box(),
            ),
            width="100%",
            align="center",
        ),
        custom_month_calendar(
            year=year,
            month=month,
            on_click_day=CalendarState.handle_day_click,
        ),
        spacing="2",
        align="center",
        width="100%",
        padding="2",
    )


def flag_selector() -> rx.Component:
    """Dynamic flag selector based on user role with quota information."""
    
    def flag_option(flag_tuple: rx.Var) -> rx.Component:
        """Create an option element for a flag with disabled state for exhausted quotas."""
        flag_value = flag_tuple[0].to(str)
        flag_label = flag_tuple[1].to(str)
        
        # Check if this is a disabled option (ends with _DISABLED)
        is_disabled = flag_value.contains("_DISABLED")
        
        return rx.el.option(
            flag_label,
            value=rx.cond(is_disabled, "", flag_value),  # Empty value if disabled
            disabled=is_disabled,
            style=rx.cond(
                is_disabled,
                {"color": "var(--gray-8)", "font-style": "italic"},
                {}
            )
        )
    
    return rx.el.select(
        rx.foreach(
            CalendarState.flag_choices_with_quota,
            flag_option,
        ),
        value=CalendarState.current_flag,
        on_change=CalendarState.set_current_flag,
        width="100%",
        padding="6px",
    )


def user_selector_dialog() -> rx.Component:
    """Dialog for selecting user (simulating different roles)."""
    
    def user_option(user: rx.Var) -> rx.Component:
        """Display a user option button."""
        return rx.button(
            user["name"].to(str),
            rx.cond(
                user["id"].to(str) == CalendarState.current_user_id,
                rx.icon("check", size=16),
                rx.box(),
            ),
            on_click=lambda: CalendarState.switch_user(user["id"]),
            variant="soft",
            width="100%",
            justify="between",
        )
    
    def region_group(region_tuple: rx.Var) -> rx.Component:
        """Display a region group with its users."""
        region_name = region_tuple[0]
        users = region_tuple[1]
        
        return rx.vstack(
            rx.hstack(
                rx.icon("map-pin", size=16, color="var(--gray-10)"),
                rx.text(
                    region_name.to(str),
                    size="3",
                    weight="medium",
                    color="var(--gray-11)",
                ),
                spacing="2",
                align="center",
                padding_left="8px",
            ),
            rx.foreach(users, user_option),
            spacing="2",
            width="100%",
            margin_bottom="12px",
        )
    
    def project_group(project_tuple: rx.Var) -> rx.Component:
        """Display a project group with its regions and users."""
        project_name = project_tuple[0]
        regions = project_tuple[1]
        
        return rx.vstack(
            rx.hstack(
                rx.icon("briefcase", size=16, color="var(--blue-9)"),
                rx.text(
                    project_name.to(str),
                    size="3",
                    weight="medium",
                    color="var(--blue-11)",
                ),
                spacing="2",
                align="center",
                padding_left="16px",
            ),
            rx.foreach(regions, region_group),
            spacing="2",
            width="100%",
            margin_bottom="12px",
        )
    
    def division_group(division_tuple: rx.Var) -> rx.Component:
        """Display a division group with its projects, regions, and users."""
        division_name = division_tuple[0]
        projects = division_tuple[1]
        
        return rx.vstack(
            rx.hstack(
                rx.icon("building-2", size=18),
                rx.heading(
                    division_name.to(str),
                    size="4",
                ),
                spacing="2",
                align="center",
            ),
            rx.foreach(projects, project_group),
            spacing="2",
            width="100%",
            margin_bottom="16px",
        )
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Switch User"),
            rx.dialog.description(
                "Select a user to simulate different roles and permissions.",
                size="2",
                margin_bottom="16px",
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        CalendarState.users_grouped_by_project,
                        division_group,
                    ),
                    spacing="4",
                    width="100%",
                ),
                max_height="400px",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Close",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.toggle_user_selector,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_user_selector,
    )


def comment_dialog() -> rx.Component:
    """Dialog for adding/editing comments."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Add Comment for ",
                rx.cond(
                    CalendarState.range_end_date != "",
                    rx.cond(
                        CalendarState.range_start_date == CalendarState.range_end_date,
                        CalendarState.range_start_date,
                        CalendarState.range_display_text
                    ),
                    rx.cond(
                        CalendarState.range_start_date != "",
                        CalendarState.range_display_text,
                        "selected day"
                    )
                )
            ),
            rx.dialog.description(
                rx.cond(
                    CalendarState.range_end_date != "",
                    rx.cond(
                        CalendarState.range_start_date != CalendarState.range_end_date,
                        rx.text("This will apply to all weekdays in the selected range.", size="2"),
                        rx.text("Enter your comment for this day.", size="2")
                    ),
                    rx.text("Enter your comment for this day.", size="2")
                ),
                margin_bottom="16px",
            ),
            rx.el.textarea(
                value=CalendarState.current_comment,
                on_change=CalendarState.set_current_comment,
                placeholder="Enter your comment here...",
                width="100%",
                height="120px",
                padding="8px",
            ),
            # Flag selector - dynamically filtered by role
            rx.box(
                rx.text("Flag (based on your role):", size="2", weight="bold"),
                flag_selector(),
                margin_top="8px",
            ),
            # Region selector (only for HR and only when "regional day off" is selected)
            rx.cond(
                (CalendarState.current_user_role == "hr") & (CalendarState.current_flag == "regional day off"),
                rx.box(
                    rx.text("Select Region:", size="2", weight="bold", color="var(--orange-11)"),
                    rx.el.select(
                        rx.el.option("Select a region...", value="", disabled=True, selected=rx.cond(CalendarState.selected_region == "", True, False)),
                        rx.foreach(
                            CalendarState.REGIONS,
                            lambda region: rx.el.option(region.to(str), value=region.to(str)),
                        ),
                        value=CalendarState.selected_region,
                        on_change=CalendarState.set_selected_region,
                        width="100%",
                        padding="6px",
                        margin_top="8px",
                    ),
                    rx.text(
                        "⚠️ This regional day off will only apply to employees in the selected region.",
                        size="1",
                        color="var(--orange-10)",
                        margin_top="4px",
                    ),
                    margin_top="8px",
                ),
                rx.box(),
            ),
            # Hours input (different ranges for different flags)
            rx.cond(
                CalendarState.current_flag == "project_special_worktime",
                # Project special worktime: 5.0 to 19.0 in 0.25 increments
                rx.box(
                    rx.text("Hours (5.0 - 19.0, step 0.25):", size="2", weight="bold"),
                    rx.el.input(
                        type="number",
                        step="0.25",
                        min="5.0",
                        max="19.0",
                        value=CalendarState.current_hours.to(str),
                        on_change=CalendarState.set_current_hours,
                        width="100%",
                        margin_top="8px",
                        padding="6px",
                    ),
                    rx.text(
                        "⚠️ This will set special project worktime and propagate to all employees in the project.",
                        size="1",
                        color="var(--cyan-10)",
                        margin_top="4px",
                    ),
                ),
                # Blank flag or other: 0-12 hours in 0.5 increments (only for blank)
                rx.box(
                    rx.text("Hours (0 - 12, step 0.25):", size="2", weight="bold"),
                    rx.el.input(
                        type="number",
                        step="0.25",
                        min="0",
                        max="12",
                        value=CalendarState.current_hours.to(str),
                        on_change=CalendarState.set_current_hours,
                        width="100%",
                        margin_top="8px",
                        padding="6px",
                        disabled=rx.cond(CalendarState.current_flag != "", True, False),
                    ),
                ),
            ),
            rx.flex(
                rx.button(
                    rx.icon("history"),
                    "View History",
                    on_click=CalendarState.open_history_dialog,
                    variant="soft",
                    color_scheme="gray",
                    disabled=rx.cond(
                        CalendarState.selected_date != "",
                        rx.cond(
                            CalendarState.history_entries_for_selected.length() == 0,
                            True,
                            False
                        ),
                        True
                    ),
                ),
                rx.spacer(),
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_comment_dialog,
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Save",
                        on_click=CalendarState.save_comment,
                        color_scheme="blue",
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="between",
                width="100%",
            ),
        ),
        open=CalendarState.show_comment_dialog,
    )


def history_dialog() -> rx.Component:
    """Dialog showing history of changes for a specific date."""
    
    def history_entry_card(entry: rx.Var) -> rx.Component:
        """Display a single history entry."""
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(entry["timestamp"].to(str), color_scheme="gray", size="1"),
                    rx.badge(entry["action"].to(str), color_scheme="blue", size="1"),
                    rx.badge(
                        rx.cond(
                            entry.get("user", rx.Var.create("Unknown")).to(str) != "Unknown",
                            entry.get("user", rx.Var.create("Unknown")).to(str),
                            "Unknown User"
                        ),
                        color_scheme="purple",
                        size="1"
                    ),
                    rx.cond(
                        entry.get("propagated_by", rx.Var.create("")).to(str) != "",
                        rx.badge(
                            rx.hstack(
                                rx.icon("megaphone", size=12),
                                rx.text("Propagated by", size="1"),
                                rx.text(entry.get("propagated_by", rx.Var.create("")).to(str), size="1"),
                                spacing="1",
                                align="center",
                            ),
                            color_scheme="orange",
                            size="1",
                        ),
                        rx.box(),
                    ),
                    spacing="2",
                ),
                rx.box(
                    rx.text("Comment:", weight="bold", size="2"),
                    rx.text(entry["comment"].to(str), size="2"),
                    margin_top="8px",
                ),
                rx.box(
                    rx.text("Flag:", weight="bold", size="2"),
                    rx.text(rx.cond(entry["flag"].to(str) == "", "(blank)", entry["flag"].to(str)), size="2"),
                    margin_top="4px",
                ),
                rx.box(
                    rx.text("Hours:", weight="bold", size="2"),
                    rx.text(entry["hours"].to(str), size="2"),
                    margin_top="4px",
                ),
                spacing="2",
                align="start",
            ),
            width="100%",
            margin_bottom="12px",
        )
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "History for ",
                rx.cond(
                    CalendarState.selected_date != "",
                    CalendarState.selected_date,
                    "selected day",
                )
            ),
            rx.dialog.description(
                "All changes made to this date (newest first).",
                size="2",
                margin_bottom="16px",
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        CalendarState.history_entries_for_selected,
                        history_entry_card,
                    ),
                    spacing="2",
                    width="100%",
                ),
                max_height="400px",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Close",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_history_dialog,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="600px",
        ),
        open=CalendarState.show_history_dialog,
    )


def export_button() -> rx.Component:
    """Buttons to export calendar - JSON for all, Image for managers/HR."""
    return rx.hstack(
        rx.button(
            rx.icon("download", size=16),
            "JSON",
            on_click=CalendarState.export_to_json,
            size="2",
            color_scheme="green",
            variant="soft",
        ),
        rx.cond(
            CalendarState.current_user_role != "employee",
            rx.button(
                rx.icon("image", size=16),
                "Image",
                on_click=CalendarState.open_export_image_dialog,
                size="2",
                color_scheme="blue",
                variant="soft",
            ),
            rx.box(),
        ),
        spacing="2",
    )


def company_holidays_dialog() -> rx.Component:
    """Dialog listing all company-wide holidays set by HR."""
    def holiday_row(item: rx.Var) -> rx.Component:
        return rx.hstack(
            rx.text(item[0].to(str), size="2"),
            rx.badge(item[1].to(str), size="2", color_scheme="orange"),
            justify="between",
            width="100%",
        )
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Company Holidays (2026)"),
            rx.dialog.description(
                "Company-wide holidays applied to all calendars by HR.",
                size="2",
                margin_bottom="12px",
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.cond(
                        CalendarState.company_holidays_list.length() == 0,
                        rx.text("No company holidays set.", size="2", color="gray"),
                        rx.foreach(CalendarState.company_holidays_list, holiday_row),
                    ),
                    spacing="2",
                    width="100%",
                ),
                max_height="360px",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Close",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_company_holidays_dialog,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="520px",
        ),
        open=CalendarState.show_company_holidays_dialog,
    )


def hr_self_validate_dialog() -> rx.Component:
    """Confirmation dialog for HR to validate their own calendar."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Validate Your Calendar"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        "You are about to validate your own calendar.",
                        size="2",
                    ),
                    rx.text(
                        "✓ This will make your calendar live and visible to you.",
                        size="2",
                        color="var(--green-10)",
                        margin_top="8px",
                    ),
                    rx.text(
                        "Do you want to proceed?",
                        size="2",
                        weight="bold",
                        margin_top="8px",
                    ),
                    spacing="2",
                ),
                margin_bottom="16px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_hr_self_validate_dialog,
                    ),
                ),
                rx.button(
                    "Validate",
                    on_click=CalendarState.hr_self_validate_calendar,
                    color_scheme="green",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="450px",
        ),
        open=CalendarState.show_hr_self_validate_dialog,
    )


def manager_validate_dialog() -> rx.Component:
    """Confirmation dialog for manager to validate a calendar."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Validate Calendar"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        f"You are about to validate the calendar for {CalendarState.viewed_user_name}.",
                        size="2",
                    ),
                    rx.text(
                        "✓ This will send the calendar back to HR with 'Validated by Manager' status.",
                        size="2",
                        color="var(--blue-10)",
                        margin_top="8px",
                    ),
                    rx.text(
                        "Do you want to proceed?",
                        size="2",
                        weight="bold",
                        margin_top="8px",
                    ),
                    spacing="2",
                ),
                margin_bottom="16px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_manager_validate_dialog,
                    ),
                ),
                rx.button(
                    "Validate",
                    on_click=CalendarState.manager_validate_calendar,
                    color_scheme="blue",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_manager_validate_dialog,
    )


def hr_final_validate_dialog() -> rx.Component:
    """Confirmation dialog for HR final validation."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Final Validation"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        f"You are about to finalize the calendar for {CalendarState.viewed_user_name}.",
                        size="2",
                    ),
                    rx.text(
                        "✓ This will make the calendar LIVE and visible to the employee.",
                        size="2",
                        color="var(--green-10)",
                        weight="bold",
                        margin_top="8px",
                    ),
                    rx.text(
                        "Do you want to proceed?",
                        size="2",
                        weight="bold",
                        margin_top="8px",
                    ),
                    spacing="2",
                ),
                margin_bottom="16px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_hr_final_validate_dialog,
                    ),
                ),
                rx.button(
                    "Finalize & Publish",
                    on_click=CalendarState.hr_final_validate_calendar,
                    color_scheme="green",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_hr_final_validate_dialog,
    )


def status_history_dialog() -> rx.Component:
    """Dialog showing full validation status change history."""
    def history_row(entry: rx.Var) -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(entry["timestamp"].to(str), size="1", color_scheme="gray"),
                    rx.badge(entry["actor"].to(str), size="1", color_scheme="purple"),
                    rx.badge(entry["actor_role"].to(str).upper(), size="1", color_scheme="blue"),
                    spacing="2",
                ),
                rx.hstack(
                    rx.text("From:", size="2", weight="medium"),
                    rx.badge(entry["from_status"].to(str), size="2", color_scheme="orange"),
                    rx.icon("arrow-right", size=16),
                    rx.text("To:", size="2", weight="medium"),
                    rx.badge(entry["to_status"].to(str), size="2", color_scheme="green"),
                    spacing="2",
                    align="center",
                ),
                rx.cond(
                    entry["changes_summary"].to(str) != "",
                    rx.text(
                        entry["changes_summary"].to(str),
                        size="2",
                        color="var(--gray-11)",
                        style={"font-style": "italic"},
                    ),
                    rx.box(),
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            width="100%",
            margin_bottom="8px",
        )
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Status Change History"),
            rx.dialog.description(
                f"Validation history for {CalendarState.viewed_user_name}",
                size="2",
                margin_bottom="12px",
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.cond(
                        CalendarState.status_history_for_viewed.length() == 0,
                        rx.text("No status changes yet.", size="2", color="gray"),
                        rx.foreach(CalendarState.status_history_for_viewed, history_row),
                    ),
                    spacing="2",
                    width="100%",
                ),
                max_height="500px",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Close",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_status_history_dialog,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
            ),
            max_width="700px",
        ),
        open=CalendarState.show_status_history_dialog,
    )


def bulk_hours_dialog() -> rx.Component:
    """Dialog for bulk-setting hours for a month (Manager/HR only)."""

    # Generate time options from 5.0 to 19.0 in 0.25 increments
    def time_option(hours: float) -> rx.Component:
        """Create a time option."""
        # Convert to hours:minutes format
        h = int(hours)
        m = int((hours - h) * 60)
        label = f"{h:02d}:{m:02d} ({hours}h)"
        return rx.el.option(label, value=str(hours))
    
    # Create list of time values
    time_values = [5.0 + (i * 0.25) for i in range(57)]  # 5.0 to 19.0 in 0.25 steps
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(
                "Bulk Set Work Hours - ",
                rx.cond(
                    CalendarState.selected_month > 0,
                    CalendarState.get_month_name,
                    "Unknown"
                ),
                " 2026"
            ),
            rx.dialog.description(
                "Set standard work hours for all weekdays in this month. This will apply to all users in your visible scope.",
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                # Monday-Thursday hours
                rx.box(
                    rx.text("Monday - Thursday:", size="3", weight="bold"),
                    rx.el.select(
                        *[time_option(val) for val in time_values],
                        value=CalendarState.bulk_hours_mon_thu.to(str),
                        on_change=CalendarState.set_bulk_hours_mon_thu,
                        width="100%",
                        padding="8px",
                        margin_top="8px",
                    ),
                    width="100%",
                ),
                # Friday hours
                rx.box(
                    rx.text("Friday:", size="3", weight="bold"),
                    rx.el.select(
                        *[time_option(val) for val in time_values],
                        value=CalendarState.bulk_hours_fri.to(str),
                        on_change=CalendarState.set_bulk_hours_fri,
                        width="100%",
                        padding="8px",
                        margin_top="8px",
                    ),
                    width="100%",
                    margin_top="12px",
                ),
                # Apply to all months checkbox
                rx.box(
                    rx.checkbox(
                        "Apply to all 12 months (entire year)",
                        checked=CalendarState.bulk_apply_to_all_months,
                        on_change=CalendarState.set_bulk_apply_to_all_months,
                        size="2",
                    ),
                    margin_top="16px",
                    padding="12px",
                    background="var(--purple-2)",
                    border_radius="6px",
                ),
                # Info message
                rx.box(
                    rx.text(
                        "ℹ️ Only weekdays without flags will be updated. Days with holidays/vacation flags will be skipped.",
                        size="2",
                        color="var(--blue-10)",
                    ),
                    margin_top="8px",
                    padding="12px",
                    background="var(--blue-2)",
                    border_radius="6px",
                ),
                spacing="2",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_bulk_hours_dialog,
                    ),
                ),
                rx.button(
                    "Apply",
                    on_click=CalendarState.preview_bulk_hours,
                    color_scheme="blue",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_bulk_hours_dialog,
    )


def bulk_hours_confirmation_dialog() -> rx.Component:
    """Confirmation dialog when bulk hours will overwrite existing data."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Confirm Bulk Hours Update"),
            rx.dialog.description(
                rx.vstack(
                    rx.text(
                        f"This will update {CalendarState.bulk_affected_days_count.to(str)} day(s) across all visible users.",
                        size="2",
                    ),
                    rx.text(
                        f"⚠️ {CalendarState.bulk_overwrite_count.to(str)} day(s) already have hours set.",
                        size="2",
                        weight="bold",
                        color="var(--orange-11)",
                    ),
                    rx.text(
                        "How do you want to handle conflicts?",
                        size="2",
                        weight="bold",
                        margin_top="12px",
                    ),
                    spacing="2",
                ),
                margin_bottom="16px",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_bulk_hours_dialog,
                    ),
                ),
                rx.button(
                    "Skip Conflicts",
                    on_click=CalendarState.bulk_hours_skip,
                    color_scheme="blue",
                ),
                rx.button(
                    "Overwrite All",
                    on_click=CalendarState.bulk_hours_overwrite,
                    color_scheme="orange",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_bulk_hours_confirmation,
    )


def quota_manager_dialog() -> rx.Component:
    """Dialog for managers/HR to set vacation quotas."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Manage Vacation Quotas"),
            rx.dialog.description(
                "Set maximum allowed days for vacation and extra days off. These quotas only apply to calendars that are not yet validated (LIVE).",
                margin_bottom="16px",
            ),
            rx.vstack(
                # Global vacation quota
                rx.box(
                    rx.heading("Company-Wide Vacation Quota", size="3", margin_bottom="8px"),
                    rx.text(
                        "This quota applies to all employees for the 'on vacation' flag.",
                        size="2",
                        color="var(--gray-11)",
                        margin_bottom="8px",
                    ),
                    rx.hstack(
                        rx.text("Maximum Days:", size="2", weight="bold", width="120px"),
                        rx.el.input(
                            type="number",
                            value=CalendarState.temp_vacation_quota.to(str),
                            on_change=CalendarState.set_temp_vacation_quota,
                            min="0",
                            max="365",
                            step="0.5",
                            width="100px",
                            padding="6px",
                        ),
                        rx.text("days", size="2", color="var(--gray-11)"),
                        spacing="2",
                        align="center",
                    ),
                    padding="12px",
                    background="var(--purple-2)",
                    border_radius="6px",
                    margin_bottom="16px",
                ),
                
                # Per-user extra days quota (when editing specific user)
                rx.cond(
                    CalendarState.editing_user_id != "",
                    rx.box(
                        rx.heading("Extra Days Off Quota", size="3", margin_bottom="8px"),
                        rx.text(
                            f"Per-user quota for the 'extra day off' flag (User: {CalendarState.viewed_user_name}).",
                            size="2",
                            color="var(--gray-11)",
                            margin_bottom="8px",
                        ),
                        rx.hstack(
                            rx.text("Maximum Days:", size="2", weight="bold", width="120px"),
                            rx.el.input(
                                type="number",
                                value=CalendarState.temp_extra_days_quota.to(str),
                                on_change=CalendarState.set_temp_extra_days_quota,
                                min="0",
                                max="100",
                                step="0.5",
                                width="100px",
                                padding="6px",
                            ),
                            rx.text("days", size="2", color="var(--gray-11)"),
                            spacing="2",
                            align="center",
                        ),
                        padding="12px",
                        background="var(--gray-2)",
                        border_radius="6px",
                    ),
                    rx.text(
                        "💡 Tip: Click 'Manage Quotas' from a user's calendar to set their extra days quota.",
                        size="2",
                        color="var(--blue-10)",
                        style={"font-style": "italic"},
                    ),
                ),
                
                spacing="3",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_quota_manager_dialog,
                    ),
                ),
                rx.dialog.close(
                    rx.button(
                        "Save Settings",
                        on_click=CalendarState.save_quota_settings,
                        color_scheme="purple",
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_quota_manager_dialog,
    )


def calendar_status_badge() -> rx.Component:
    """Badge showing calendar validation status in header."""
    def get_status_color(status: str) -> str:
        """Get color scheme based on status."""
        status_colors = {
            "draft": "gray",
            "pending_manager_validation": "orange", 
            "validated_by_manager": "blue",
            "validated": "green"
        }
        return status_colors.get(status, "gray")
    
    def get_status_label(status: str) -> str:
        """Get human-readable status label."""
        labels = {
            "draft": "Draft",
            "pending_manager_validation": "Pending Manager",
            "validated_by_manager": "Manager OK",
            "validated": "Validated"
        }
        return labels.get(status, status)
    
    return rx.cond(
        CalendarState.viewed_user_id != CalendarState.current_user_id,
        rx.badge(
            rx.icon("shield-check", size=14),
            get_status_label(CalendarState.viewed_calendar_status),
            size="2",
            color_scheme=get_status_color(CalendarState.viewed_calendar_status),
        ),
        rx.box(),
    )


def calendar_status_panel() -> rx.Component:
    """Detailed status panel above calendar grid with action buttons."""
    
    def get_status_info() -> rx.Component:
        """Status information with icon and description."""
        return rx.cond(
            CalendarState.viewed_calendar_status == CalendarState.STATUS_DRAFT,
            rx.hstack(
                rx.icon("file-edit", size=24, color="var(--gray-9)"),
                rx.vstack(
                    rx.text("Draft", size="4", weight="bold"),
                    rx.text("Calendar is being prepared", size="2", color="gray"),
                    spacing="1",
                    align="start",
                ),
                spacing="3",
            ),
            rx.cond(
                CalendarState.viewed_calendar_status == CalendarState.STATUS_PENDING_MANAGER,
                rx.hstack(
                    rx.icon("clock", size=24, color="var(--orange-9)"),
                    rx.vstack(
                        rx.text("Pending Manager Validation", size="4", weight="bold", color="var(--orange-11)"),
                        rx.text("Waiting for manager review", size="2", color="gray"),
                        spacing="1",
                        align="start",
                    ),
                    spacing="3",
                ),
                rx.cond(
                    CalendarState.viewed_calendar_status == CalendarState.STATUS_VALIDATED_BY_MANAGER,
                    rx.hstack(
                        rx.icon("user-check", size=24, color="var(--blue-9)"),
                        rx.vstack(
                            rx.text("Validated by Manager", size="4", weight="bold", color="var(--blue-11)"),
                            rx.text("Ready for HR final validation", size="2", color="gray"),
                            spacing="1",
                            align="start",
                        ),
                        spacing="3",
                    ),
                    rx.hstack(
                        rx.icon("check-circle", size=24, color="var(--green-9)"),
                        rx.vstack(
                            rx.text("Validated (Live)", size="4", weight="bold", color="var(--green-11)"),
                            rx.text("Calendar is live and visible to user", size="2", color="gray"),
                            spacing="1",
                            align="start",
                        ),
                        spacing="3",
                    ),
                ),
            ),
        )
    
    def action_buttons() -> rx.Component:
        """Action buttons based on current user role and calendar status."""
        return rx.hstack(
            # HR self-validate button (only for HR viewing their own calendar)
            rx.cond(
                (CalendarState.current_user_role == "hr") & (CalendarState.viewed_user_id == CalendarState.current_user_id) & (CalendarState.viewed_calendar_status != CalendarState.STATUS_VALIDATED),
                rx.button(
                    rx.icon("shield-check", size=16),
                    "Validate My Calendar",
                    on_click=CalendarState.open_hr_self_validate_dialog,
                    color_scheme="green",
                    size="2",
                ),
                rx.box(),
            ),
            # Manager validate button
            rx.cond(
                (CalendarState.current_user_role == "manager") & (CalendarState.viewed_user_id != CalendarState.current_user_id),
                rx.button(
                    rx.icon("user-check", size=16),
                    "Validate Calendar",
                    on_click=CalendarState.open_manager_validate_dialog,
                    color_scheme="blue",
                    size="2",
                ),
                rx.box(),
            ),
            # HR final validate button (only when status is validated_by_manager)
            rx.cond(
                (CalendarState.current_user_role == "hr") & (CalendarState.viewed_user_id != CalendarState.current_user_id) & (CalendarState.viewed_calendar_status == CalendarState.STATUS_VALIDATED_BY_MANAGER),
                rx.button(
                    rx.icon("check-circle", size=16),
                    "Final Validation",
                    on_click=CalendarState.open_hr_final_validate_dialog,
                    color_scheme="green",
                    size="2",
                ),
                rx.box(),
            ),
            # View history button
            rx.button(
                rx.icon("history", size=16),
                "View Status History",
                on_click=CalendarState.open_status_history_dialog,
                variant="soft",
                color_scheme="gray",
                size="2",
            ),
            # Export button (HR and managers only)
            rx.button(
                rx.icon("download", size=16),
                "Export",
                on_click=CalendarState.open_export_dialog,
                variant="soft",
                color_scheme="blue",
                size="2",
            ),
            # Import button (HR and managers only)
            rx.button(
                rx.icon("upload", size=16),
                "Import",
                on_click=CalendarState.open_import_dialog,
                variant="soft",
                color_scheme="green",
                size="2",
            ),
            spacing="2",
        )
    
    # Only show panel for managers and HR
    return rx.cond(
        CalendarState.current_user_role != "employee",
        rx.card(
            rx.vstack(
                rx.hstack(
                    get_status_info(),
                    rx.spacer(),
                    action_buttons(),
                    width="100%",
                    align="center",
                ),
                spacing="2",
                width="100%",
            ),
            width="100%",
            margin_bottom="16px",
        ),
        rx.box(),
    )


def calendar_view_selector() -> rx.Component:
    """Selector for viewing different team members' calendars (Manager/HR only)."""
    
    def calendar_option(user: rx.Var) -> rx.Component:
        """Display a calendar view option."""
        return rx.button(
            user.to(dict).get("name").to(str),
            rx.cond(
                user.to(dict).get("id").to(str) == CalendarState.viewed_user_id,
                rx.icon("eye", size=14),
                rx.box(),
            ),
            on_click=lambda: CalendarState.view_user_calendar(user.to(dict).get("id")),
            variant="soft",
            size="1",
            color_scheme=rx.cond(
                user.to(dict).get("id").to(str) == CalendarState.viewed_user_id,
                "blue",
                "gray"
            ),
        )
    
    def region_group_compact(region_tuple: rx.Var) -> rx.Component:
        """Display a compact region group with user buttons."""
        region_name = region_tuple[0]
        users = region_tuple[1]
        
        return rx.vstack(
            rx.hstack(
                rx.icon("map-pin", size=12, color="var(--gray-9)"),
                rx.text(
                    region_name.to(str),
                    size="1",
                    weight="medium",
                    color="var(--gray-10)",
                ),
                spacing="1",
                align="center",
            ),
            rx.flex(
                rx.foreach(users, calendar_option),
                spacing="1",
                wrap="wrap",
            ),
            spacing="1",
            width="100%",
            margin_bottom="8px",
        )
    
    def project_group_compact(project_tuple: rx.Var) -> rx.Component:
        """Display a compact project group with regions and calendar buttons."""
        project_name = project_tuple[0]
        regions = project_tuple[1]
        
        return rx.vstack(
            rx.text(
                project_name.to(str),
                size="1",
                weight="bold",
                # color="gray",
                color="var(--blue-11)",
            ),
            rx.foreach(regions, region_group_compact),
            spacing="1",
            width="100%",
        )
    
    def division_group_compact(division_tuple: rx.Var) -> rx.Component:
        """Display a compact division group with projects and calendar buttons."""
        division_name = division_tuple[0]
        projects = division_tuple[1]
        
        return rx.vstack(
            rx.text(
                division_name.to(str),
                size="2",
                weight="bold",
                color="var(--purple-11)",
            ),
            rx.foreach(projects, project_group_compact),
            spacing="2",
            width="100%",
            margin_bottom="12px",
        )
    
    return rx.cond(
        CalendarState.current_user_role != "employee",
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("View Calendar:", size="2", weight="bold"),
                    rx.icon("chevrons-up-down", size=20, color="var(--gray-9)"),
                    on_click=CalendarState.toggle_quickview_panel,
                ),
                rx.cond(
                    CalendarState.show_quickview_panel,
                    rx.foreach(
                        CalendarState.users_grouped_by_project,
                        division_group_compact,
                    ),
                    rx.box(),
                ),
                spacing="2",
            ),
            padding="3",
            border="1px solid var(--gray-6)",
            border_radius="8px",
            background="var(--gray-2)",
        ),
        rx.box(),  # Empty box for employees
    )


def header() -> rx.Component:
    """Application header with title, user info, project badge, and export button."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                # Left: Title and instructions
                rx.vstack(
                    rx.heading(
                        "2026 Calendar",
                        size="9",
                    ),
                    rx.text(
                        "Click on weekdays (Monday-Friday) to add comments",
                        size="3",
                    ),
                    spacing="2",
                    align_items="start",
                ),
                rx.spacer(),
                # Right: Current user and controls
                rx.vstack(
                    rx.hstack(
                        rx.text("Current User:", weight="bold", size="2"),
                        rx.badge(
                            CalendarState.current_user_name,
                            color_scheme=rx.cond(
                                CalendarState.current_user_role == "hr",
                                "purple",
                                rx.cond(
                                    CalendarState.current_user_role == "manager",
                                    "blue",
                                    "gray"
                                )
                            ),
                            size="2",
                        ),
                        spacing="2",
                    ),
                    rx.button(
                        rx.icon("users", size=16),
                        "Switch User",
                        on_click=CalendarState.toggle_user_selector,
                        variant="soft",
                        size="2",
                        color_scheme="gray",
                    ),
                    spacing="2",
                    align_items="end",
                ),
                rx.hstack(
                    rx.button(
                        rx.icon("calendar"),
                        "Company Holidays",
                        on_click=CalendarState.open_company_holidays_dialog,
                        variant="soft",
                        color_scheme="orange",
                        size="2",
                    ),
                    export_button(),
                    spacing="2",
                ),
                width="100%",
                align="center",
            ),
            # Project badge and viewing info (Option B style)
            rx.hstack(
                rx.hstack(
                    rx.icon("building-2", size=20, color="var(--blue-9)"),
                    rx.text(
                        f"Project: {CalendarState.viewed_user_project_name}",
                        size="4",
                        weight="bold",
                        color="var(--blue-11)",
                    ),
                    spacing="2",
                    align="center",
                    padding="2",
                    border_radius="6px",
                    background="var(--blue-3)",
                    border="1px solid var(--blue-6)",
                ),
                rx.spacer(),
                rx.cond(
                    CalendarState.viewed_user_id != CalendarState.current_user_id,
                    rx.badge(
                        f"Viewing: {CalendarState.viewed_user_name}",
                        color_scheme="orange",
                        size="2",
                    ),
                    rx.box(),
                ),
                rx.cond(
                    CalendarState.can_edit_viewed_calendar == False,
                    rx.badge(
                        "Read-Only",
                        color_scheme="red",
                        size="2",
                    ),
                    rx.box(),
                ),
                calendar_status_badge(),
                width="100%",
                align="center",
            ),
            # Notification banner (only when viewing own calendar)
            rx.cond(
                CalendarState.viewed_user_id == CalendarState.current_user_id,
                rx.cond(
                    CalendarState.notifications_for_viewed.length() > 0,
                    rx.card(
                        rx.hstack(
                            rx.icon("megaphone", color="var(--orange-9)"),
                            rx.text(
                                CalendarState.notifications_for_viewed[0].to(str),
                                size="2",
                            ),
                            rx.spacer(),
                            rx.button(
                                "Dismiss",
                                size="1",
                                variant="soft",
                                color_scheme="gray",
                                on_click=CalendarState.dismiss_notifications_for_viewed,
                            ),
                            align="center",
                            width="100%",
                        ),
                        width="100%",
                        background="var(--orange-2)",
                        padding="8px",
                    ),
                    rx.box(),
                ),
                rx.box(),
            ),
            # Calendar view selector (Manager/HR only)
            calendar_view_selector(),
            spacing="3",
            width="100%",
            padding_x="6",
            padding_y="4",
        ),
        width="100%",
    )


def calendar_grid() -> rx.Component:
    """Grid layout displaying all 12 months of 2026."""
    return rx.box(
        # Warning banner for non-validated calendars (employees only)
        rx.cond(
            ~CalendarState.can_employee_view_own_calendar,
            rx.callout(
                rx.callout.text(
                    rx.text("Your calendar is being prepared and must be validated before you can interact with it.", weight="bold"),
                ),
                icon="lock",
                color_scheme="orange",
                size="3",
                margin_bottom="6",
            ),
            rx.box(),
        ),
        # Calendar grid (always shown, but disabled for non-validated employees)
        rx.box(
            rx.grid(
                *[month_calendar(month) for month in range(1, 13)],
                columns="4",
                spacing="4",
                width="100%",
            ),
            # Legend showing flag colors (hardcoded to avoid Var issues)
            rx.box(
                rx.hstack(
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "transparent"}),
                        rx.text("(blank)", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#e53e3e"}),
                        rx.text("Offered vacation: client closed", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#dd6b20"}),
                        rx.text("Offered vacation: holiday season", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#3182ce"}),
                        rx.text("Sick leave", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#805ad5"}),
                        rx.text("Vacation", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#2f855a"}),
                        rx.text("Training", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#d53f8c"}),
                        rx.text("Stand-by", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    rx.hstack(
                        rx.box(style={"width": "14px", "height": "14px", "border_radius": "50%", "background": "#718096"}),
                        rx.text("Short-time work", size="2"),
                        spacing="3",
                        align="center",
                    ),
                    spacing="4",
                ),
                margin_top="6",
            ),
            # Apply gray overlay and disable pointer events for non-validated calendars
            opacity=rx.cond(CalendarState.can_employee_view_own_calendar, "1", "0.4"),
            style=rx.cond(
                CalendarState.can_employee_view_own_calendar,
                {},
                {"pointer-events": "none", "user-select": "none"}
            ),
        ),
        padding="6",
        width="100%",
    )


def stats_footer() -> rx.Component:
    """Footer showing statistics about comments."""
    return rx.box(
        rx.hstack(
            rx.badge(
                rx.icon("message-square", size=16),
                rx.text(CalendarState.comment_count, " comments"),
                size="2",
                variant="soft",
                color_scheme="blue",
            ),
            rx.text(
                "Total comments added to the calendar",
                size="2",
            ),
            spacing="3",
            align="center",
            justify="center",
        ),
        width="100%",
        padding="4",
    )


def export_dialog() -> rx.Component:
    """Dialog for exporting calendar(s) to JSON."""
    
    def user_checkbox(user: dict) -> rx.Component:
        """Checkbox for selecting user in bulk export."""
        return rx.box(
            rx.checkbox(
                rx.text(user["name"].to(str), " (", user["role"].to(str), ")", size="2"),
                checked=CalendarState.export_bulk_user_ids.contains(user["id"].to(str)),
                on_change=lambda: CalendarState.toggle_bulk_export_user(user["id"].to(str)),
            ),
            margin_bottom="4px",
        )
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Export Calendar to JSON"),
            rx.dialog.description(
                "Export calendar data to a JSON file for backup or transfer.",
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                # Export target selection
                rx.text("Select Export Target:", size="3", weight="bold", margin_bottom="8px"),
                rx.radio_group.root(
                    rx.vstack(
                        rx.radio_group.item(
                            "Currently viewed user's calendar",
                            value="viewed",
                        ),
                        rx.radio_group.item(
                            "My own calendar",
                            value="self",
                        ),
                        rx.radio_group.item(
                            "Bulk export (select multiple users)",
                            value="bulk",
                        ),
                        spacing="2",
                    ),
                    value=CalendarState.export_target,
                    on_change=CalendarState.set_export_target,
                ),
                
                # Bulk user selection (shown only when bulk is selected)
                rx.cond(
                    CalendarState.export_target == "bulk",
                    rx.box(
                        rx.text(
                            "Select users to export:",
                            size="3",
                            weight="bold",
                            margin_top="16px",
                            margin_bottom="8px",
                        ),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(CalendarState.visible_users, user_checkbox),
                                spacing="1",
                                align="start",
                            ),
                            max_height="300px",
                            width="100%",
                        ),
                    ),
                    rx.box(),
                ),
                
                spacing="2",
                width="100%",
            ),
            
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_export_dialog,
                    ),
                ),
                rx.button(
                    rx.icon("download", size=16),
                    "Export JSON",
                    on_click=CalendarState.export_calendar,
                    color_scheme="blue",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="600px",
        ),
        open=CalendarState.show_export_dialog,
    )


def import_dialog() -> rx.Component:
    """Dialog for importing calendar from JSON file."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Import Calendar from JSON"),
            rx.dialog.description(
                "Import calendar data from a JSON file. This will create a new user or update an existing user's calendar.",
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                rx.text("Upload JSON File:", size="3", weight="bold", margin_bottom="8px"),
                rx.upload(
                    rx.vstack(
                        rx.button(
                            rx.icon("upload", size=20),
                            "Select JSON File",
                            color_scheme="blue",
                            variant="soft",
                        ),
                        rx.text(
                            "Drag and drop or click to select",
                            size="2",
                            color="gray",
                        ),
                        spacing="2",
                        align="center",
                    ),
                    accept={
                        "application/json": [".json"],
                    },
                    max_files=1,
                    on_drop=CalendarState.handle_import_file_upload(rx.upload_files()),
                ),
                
                # Validation errors
                rx.cond(
                    CalendarState.import_validation_errors.length() > 0,
                    rx.box(
                        rx.callout(
                            rx.vstack(
                                rx.foreach(
                                    CalendarState.import_validation_errors,
                                    lambda err: rx.text(err, size="2"),
                                ),
                                spacing="1",
                            ),
                            icon="alert-triangle",
                            color_scheme="red",
                            size="2",
                        ),
                        margin_top="16px",
                    ),
                    rx.box(),
                ),
                
                spacing="2",
                width="100%",
            ),
            
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_import_dialog,
                    ),
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="600px",
        ),
        open=CalendarState.show_import_dialog,
    )


def import_confirmation_dialog() -> rx.Component:
    """Confirmation dialog showing import preview before applying."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Confirm Calendar Import"),
            rx.dialog.description(
                "Review the import details before applying changes.",
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                # Import action (create or update)
                rx.cond(
                    CalendarState.import_preview_data["is_new_user"].to(bool),
                    rx.callout(
                        rx.callout.text(
                            rx.text("Creating NEW user: ", weight="bold"),
                            CalendarState.import_preview_data["user_name"].to(str),
                        ),
                        icon="user-plus",
                        color_scheme="green",
                        size="2",
                    ),
                    rx.callout(
                        rx.callout.text(
                            rx.text("Updating EXISTING user: ", weight="bold"),
                            CalendarState.import_preview_data["user_name"].to(str),
                        ),
                        icon="user-check",
                        color_scheme="blue",
                        size="2",
                    ),
                ),
                
                # User details
                rx.box(
                    rx.text("User Details:", size="3", weight="bold", margin_bottom="8px"),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Role:", size="2", weight="bold"),
                            rx.badge(
                                CalendarState.import_preview_data["user_role"].to(str),
                                size="1",
                            ),
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.text("Project:", size="2", weight="bold"),
                            rx.text(
                                CalendarState.import_preview_data["project"].to(dict)["name"].to(str),
                                size="2",
                            ),
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.text("Region:", size="2", weight="bold"),
                            rx.text(
                                CalendarState.import_preview_data["region"].to(str),
                                size="2",
                            ),
                            spacing="2",
                        ),
                        rx.hstack(
                            rx.text("Days to import:", size="2", weight="bold"),
                            rx.text(
                                CalendarState.import_preview_data["days_count"].to(str),
                                size="2",
                            ),
                            spacing="2",
                        ),
                        spacing="2",
                        align="start",
                    ),
                    margin_top="12px",
                ),
                
                # HR flags warning for existing users
                rx.cond(
                    CalendarState.import_preview_data["is_new_user"].to(bool) == False,
                    rx.cond(
                        CalendarState.import_preview_data["hr_flags_in_import"].to(list).length() > 0,
                        rx.callout(
                            rx.callout.text(
                                rx.text("Note: ", weight="bold"),
                                f"HR-only flags will be skipped (existing HR flags preserved).",
                            ),
                            icon="info",
                            color_scheme="orange",
                            size="2",
                        ),
                        rx.box(),
                    ),
                    rx.box(),
                ),
                
                # New user: HR flags will be inherited
                rx.cond(
                    CalendarState.import_preview_data["is_new_user"].to(bool),
                    rx.callout(
                        rx.callout.text(
                            rx.text("Note: ", weight="bold"),
                            "HR-defined holidays will be automatically inherited from the project.",
                        ),
                        icon="info",
                        color_scheme="blue",
                        size="2",
                    ),
                    rx.box(),
                ),
                
                spacing="3",
                width="100%",
            ),
            
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_import_dialog,
                    ),
                ),
                rx.button(
                    rx.icon("check", size=16),
                    "Confirm Import",
                    on_click=CalendarState.confirm_import_calendar,
                    color_scheme="green",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="600px",
        ),
        open=CalendarState.show_import_confirmation_dialog,
    )


def summary_panel() -> rx.Component:
    """Sidebar panel showing hours/days summary and flag counts for viewed user."""
    
    # Month names for display
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    def monthly_summary_row(month: int) -> rx.Component:
        """Display a row for monthly summary."""
        hours = CalendarState.monthly_hours_summary[month]
        days = CalendarState.monthly_days_summary[month]
        
        return rx.hstack(
            rx.text(month_names[month - 1], size="2", width="40px"),
            rx.cond(
                CalendarState.show_summary_in_days,
                rx.text(f"{days.to(float):.2f} days", size="2", weight="medium"),
                rx.text(f"{hours.to(float):.2f}h", size="2", weight="medium"),
            ),
            justify="between",
            width="100%",
            padding="4px 8px",
        )
    
    def flag_count_row(flag_name: str, count: int) -> rx.Component:
        """Display a row for flag count."""
        return rx.hstack(
            rx.text(flag_name, size="2"),
            rx.badge(count.to(str), size="1", color_scheme="blue"),
            justify="between",
            width="100%",
            padding="4px 8px",
        )
    
    return rx.box(
        rx.vstack(
            # Header
            rx.heading("Summary", size="4"),
            
            # Conversion ratio setting
            rx.hstack(
                rx.text("Hours/Day Ratio:", size="2", weight="bold"),
                rx.el.input(
                    type="number",
                    value=CalendarState.hours_to_days_ratio.to(str),
                    on_change=CalendarState.set_hours_to_days_ratio,
                    min="1",
                    max="24",
                    step="0.5",
                    width="80px",
                    padding="4px",
                ),
                spacing="2",
                align="center",
            ),
            
            # Toggle button
            rx.button(
                rx.cond(
                    CalendarState.show_summary_in_days,
                    "Switch to Hours",
                    "Switch to Days",
                ),
                on_click=CalendarState.toggle_summary_display,
                size="2",
                variant="soft",
                width="100%",
            ),
            
            # Yearly total
            rx.box(
                rx.hstack(
                    rx.text("Year Total:", size="3", weight="bold"),
                    rx.cond(
                        CalendarState.show_summary_in_days,
                        rx.text(
                            f"{CalendarState.yearly_days_total.to(float):.2f} days",
                            size="3",
                            weight="bold",
                            color="var(--blue-11)",
                        ),
                        rx.text(
                            f"{CalendarState.yearly_hours_total.to(float):.2f}h",
                            size="3",
                            weight="bold",
                            color="var(--blue-11)",
                        ),
                    ),
                    justify="between",
                    width="100%",
                ),
                padding="12px",
                background="var(--blue-2)",
                border_radius="6px",
                margin_top="8px",
                margin_bottom="8px",
            ),
            
            # Monthly breakdown (collapsible) czo
            rx.box(
                rx.hstack(
                    rx.icon("chevrons-up-down", size=20, color="var(--gray-9)"),
                    rx.text("Monthly Breakdown", icon="chevrons-up-down", size="3", weight="bold",),
                    on_click=CalendarState.toggle_monthly_breakdown,
                ),
                rx.cond(
                    CalendarState.show_monthly_breakdown,
                    rx.vstack(
                        *[monthly_summary_row(m) for m in range(1, 13)],
                        spacing="1",
                        width="100%",
                    ),
                    rx.box(),
                ),                
                padding="12px",
                background="var(--gray-2)",
                margin_top="8px",
            ),
            
            # Flag counts section
            rx.heading("Flag Counts", size="4", margin_top="16px"),
            rx.vstack(
                flag_count_row("National Day Off", CalendarState.flag_counts["national day off"]),
                flag_count_row("Akkodis Day Off", CalendarState.flag_counts["Akkodis offered day off"]),
                flag_count_row("Regional Day Off", CalendarState.flag_counts["regional day off"]),
                flag_count_row("Extra Day Off", CalendarState.flag_counts["extra day off"]),
                flag_count_row("On Vacation", CalendarState.flag_counts["on vacation"]),
                spacing="1",
                width="100%",
            ),
            
            # Quota information section (only visible when calendar is not LIVE)
            rx.cond(
                CalendarState.viewed_calendar_status != CalendarState.STATUS_VALIDATED,
                rx.box(
                    rx.heading("Vacation Quotas", size="4", margin_top="16px"),
                    rx.vstack(
                        # Vacation remaining
                        rx.hstack(
                            rx.icon("plane", size=16, color="var(--purple-10)"),
                            rx.text("On Vacation:", size="2", weight="bold"),
                            rx.text(
                                f"{CalendarState.vacation_remaining.to(int)} / {CalendarState.vacation_quota_global.to(int)} days",
                                size="2",
                                color=rx.cond(
                                    CalendarState.vacation_remaining > 0,
                                    "var(--green-11)",
                                    "var(--red-11)"
                                ),
                            ),
                            spacing="2",
                            align="center",
                        ),
                        # Extra days remaining
                        rx.hstack(
                            rx.icon("calendar-plus", size=16, color="var(--gray-10)"),
                            rx.text("Extra Days:", size="2", weight="bold"),
                            rx.text(
                                f"{CalendarState.extra_days_remaining.to(int)} / {CalendarState.extra_days_quota.get(CalendarState.viewed_user_id, 5.0).to(int)} days",
                                size="2",
                                color=rx.cond(
                                    CalendarState.extra_days_remaining > 0,
                                    "var(--green-11)",
                                    "var(--red-11)"
                                ),
                            ),
                            spacing="2",
                            align="center",
                        ),
                        # Manage quotas button (managers/HR only)
                        rx.cond(
                            # CalendarState.current_user_role in ["manager", "hr"],
                            CalendarState.is_hr_or_manager,
                            rx.button(
                                rx.icon("settings", size=16),
                                "Manage Quotas",
                                on_click=lambda: CalendarState.open_quota_manager_dialog(CalendarState.viewed_user_id),
                                size="2",
                                variant="soft",
                                width="100%",
                            ),
                            rx.box(),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    padding="12px",
                    background="var(--purple-2)",
                    border_radius="6px",
                    margin_top="8px",
                ),
                rx.box(),
            ),
            
            spacing="3",
            width="100%",
        ),
        padding="16px",
        border_left="1px solid var(--gray-6)",
        min_width="250px",
        max_width="300px",
        height="100%",
        overflow_y="auto",
    )


def export_image_dialog() -> rx.Component:
    """Dialog for exporting calendar as PNG or PDF."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Export Calendar as Image"),
            rx.dialog.description(
                "Export the current calendar view as an image file (landscape orientation).",
                size="2",
                margin_bottom="16px",
            ),
            rx.vstack(
                rx.text(
                    "The export will include:",
                    size="2",
                    weight="bold",
                ),
                rx.unordered_list(
                    rx.list_item("Division and Project information"),
                    rx.list_item("User name and role"),
                    rx.list_item("Full calendar grid with all entries"),
                    rx.list_item("Summary totals (hours/days)"),
                    rx.list_item("Flag counts"),
                    size="2",
                ),
                spacing="2",
                width="100%",
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancel",
                        variant="soft",
                        color_scheme="gray",
                        on_click=CalendarState.close_export_image_dialog,
                    ),
                ),
                rx.button(
                    rx.icon("image", size=16),
                    "Export PNG",
                    on_click=CalendarState.export_calendar_image_png,
                    color_scheme="blue",
                ),
                rx.button(
                    rx.icon("file-text", size=16),
                    "Export PDF",
                    on_click=CalendarState.export_calendar_image_pdf,
                    color_scheme="green",
                ),
                spacing="3",
                margin_top="16px",
                justify="end",
                width="100%",
            ),
            max_width="500px",
        ),
        open=CalendarState.show_export_image_dialog,
    )

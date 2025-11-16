"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx

from rxconfig import config
from .state import CalendarState
from .components import (
    header,
    calendar_grid,
    comment_dialog,
    history_dialog,
    user_selector_dialog,
    stats_footer,
    company_holidays_dialog,
    bulk_hours_dialog,
    bulk_hours_confirmation_dialog,
    quota_manager_dialog,
    calendar_status_panel,
    hr_self_validate_dialog,
    manager_validate_dialog,
    hr_final_validate_dialog,
    status_history_dialog,
    export_dialog,
    import_dialog,
    import_confirmation_dialog,
    summary_panel,
    export_image_dialog,
)


def index() -> rx.Component:
    """Main landing page with 2026 calendar."""
    return rx.box(
        rx.color_mode.button(position="top-right"),
        header(),
        calendar_status_panel(),
        rx.hstack(
            calendar_grid(),
            summary_panel(),
            spacing="0",
            width="100%",
            align="start",
        ),
        stats_footer(),
        comment_dialog(),
        history_dialog(),
        company_holidays_dialog(),
        bulk_hours_dialog(),
        bulk_hours_confirmation_dialog(),
        quota_manager_dialog(),
        user_selector_dialog(),
        hr_self_validate_dialog(),
        manager_validate_dialog(),
        hr_final_validate_dialog(),
        status_history_dialog(),
        export_dialog(),
        import_dialog(),
        import_confirmation_dialog(),
        export_image_dialog(),
        width="100%",
        min_height="100vh",
    )


app = rx.App()
app.add_page(index, title="2026 Calendar - Add Comments to Your Days")

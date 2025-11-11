"""State management for the calendar application."""

import json
from datetime import datetime
from typing import Any, TypedDict
import reflex as rx


class HistoryEntry(TypedDict):
    """Type definition for a history entry."""
    timestamp: str
    action: str
    comment: str
    flag: str
    hours: float


class Project(TypedDict):
    """Type definition for a project."""
    id: str
    name: str
    description: str


class User(TypedDict):
    """Type definition for a user."""
    id: str
    name: str
    role: str  # "employee", "manager", "hr"
    project_id: str  # Link to project


class CalendarState(rx.State):
    """State for managing calendar comments and interactions."""
    
    # User management
    current_user_id: str = "hr001"  # Default user (who is logged in)
    viewed_user_id: str = "hr001"  # Which user's calendar is being viewed
    show_user_selector: bool = False
    
    # Projects data
    PROJECTS: list[dict] = [
        {"id": "proj001", "name": "Atlas", "description": "Global Infrastructure Project"},
        {"id": "proj002", "name": "Phoenix", "description": "Digital Transformation Initiative"},
        {"id": "proj003", "name": "Horizon", "description": "Future Innovation Lab"},
    ]
    
    # Available regions in Spain
    REGIONS: list[str] = [
        "Andalousia",
        "Valencia", 
        "Baleares",
        "Madrid",
        "Asturias",
        "Cantabria"
    ]
    
    # Dummy users data with project and region assignments
    USERS: list[dict] = [
        # Project Atlas (6 users: 4 employees + 1 manager + 1 HR)        
        {"id": "emp001", "name": "Alice Johnson", "role": "employee", "project_id": "proj001", "region": "Madrid"},
        {"id": "emp002", "name": "Bob Smith", "role": "employee", "project_id": "proj001", "region": "Valencia"},
        {"id": "emp003", "name": "Charlie Brown", "role": "employee", "project_id": "proj001", "region": "Andalousia"},
        {"id": "emp004", "name": "Diana Prince", "role": "employee", "project_id": "proj001", "region": "Madrid"},
        {"id": "mgr001", "name": "Kevin Anderson (Manager)", "role": "manager", "project_id": "proj001", "region": "Valencia"},
        {"id": "hr001", "name": "Michael Scott (HR)", "role": "hr", "project_id": "proj001", "region": "Madrid"},
        
        # Project Phoenix (6 users: 4 employees + 1 manager + 2 HR)
        {"id": "emp005", "name": "Ethan Hunt", "role": "employee", "project_id": "proj002", "region": "Baleares"},
        {"id": "emp006", "name": "Fiona Green", "role": "employee", "project_id": "proj002", "region": "Asturias"},
        {"id": "emp007", "name": "George Wilson", "role": "employee", "project_id": "proj002", "region": "Cantabria"},
        {"id": "emp008", "name": "Hannah White", "role": "employee", "project_id": "proj002", "region": "Baleares"},
        {"id": "mgr002", "name": "Laura Martinez (Manager)", "role": "manager", "project_id": "proj002", "region": "Valencia"},
        {"id": "hr002", "name": "Nancy Drew (HR)", "role": "hr", "project_id": "proj002", "region": "Baleares"},
        {"id": "hr003", "name": "Oscar Wilde (HR)", "role": "hr", "project_id": "proj002", "region": "Asturias"},
        
        # Project Horizon (5 users: 2 employees + 1 manager + 2 HR)
        {"id": "emp009", "name": "Ian Malcolm", "role": "employee", "project_id": "proj003", "region": "Cantabria"},
        {"id": "emp010", "name": "Julia Roberts", "role": "employee", "project_id": "proj003", "region": "Madrid"},
        {"id": "mgr003", "name": "Marcus Lee (Manager)", "role": "manager", "project_id": "proj003", "region": "Andalousia"},
        {"id": "hr004", "name": "Patricia Hill (HR)", "role": "hr", "project_id": "proj003", "region": "Cantabria"},
        {"id": "hr005", "name": "Quincy Adams (HR)", "role": "hr", "project_id": "proj003", "region": "Madrid"},
    ]
    
    # Role-based flag permissions
    HR_ONLY_FLAGS = [
        "national day off",
        "Akkodis offered day off",
        "regional day off"
    ]
    
    HR_MANAGER_FLAGS = [
        "offered vacation client closed",
        "on vacation client closed",
        "extra day off",
        "on vacation"
    ]
    
    EMPLOYEE_FLAGS = [
        "extra day off",
        "on vacation"
    ]
    
    # History tracking: {user_id: {date: [entries]}} - per-user calendars
    # Each user has their own calendar linked to their project
    history: dict[str, dict[str, list[dict]]] = {}
    
    # Range selection for multiple days
    range_start_date: str = ""
    range_end_date: str = ""
    is_selecting_range: bool = False
    hovered_date: str = ""
    
    # Currently selected date (or range)
    selected_date: str = ""
    
    # Current values being edited in dialog (loaded from latest history entry)
    current_comment: str = ""
    current_flag: str = ""
    current_hours: float = 0.0
    selected_region: str = ""  # For HR: which region to apply regional day off to
    
    # Dialog states
    show_comment_dialog: bool = False
    show_history_dialog: bool = False
    show_company_holidays_dialog: bool = False
    show_bulk_hours_dialog: bool = False
    show_bulk_hours_confirmation: bool = False
    
    # Bulk hours setting (for managers/HR to set monthly work hours)
    selected_month: int = 1  # 1-12
    bulk_hours_mon_thu: float = 8.0  # Hours for Monday-Thursday
    bulk_hours_fri: float = 8.0  # Hours for Friday
    bulk_affected_days_count: int = 0  # Days that will be affected
    bulk_overwrite_count: int = 0  # Days that already have hours

    # Company-wide holidays (set by HR) and per-user notifications
    company_holidays: dict[str, str] = {}  # {date_iso: flag}
    notifications: dict[str, list[str]] = {}  # {user_id: [messages]}
    
    # Calendar validation status system
    # Status constants
    STATUS_DRAFT = "draft"
    STATUS_PENDING_MANAGER = "pending_manager_validation"
    STATUS_VALIDATED_BY_MANAGER = "validated_by_manager"
    STATUS_VALIDATED = "validated"
    
    # Calendar status per user: {user_id: status}
    calendar_status: dict[str, str] = {}
    
    # Status change history per user: {user_id: [history_entries]}
    # Each entry: {timestamp, from_status, to_status, actor, actor_role, changes_summary}
    status_history: dict[str, list[dict]] = {}
    
    # Dialog states for validation
    show_status_history_dialog: bool = False
    show_hr_self_validate_dialog: bool = False
    show_manager_validate_dialog: bool = False
    show_hr_final_validate_dialog: bool = False
    
    # Export/Import dialog states and data
    show_export_dialog: bool = False
    show_import_dialog: bool = False
    show_import_confirmation_dialog: bool = False
    export_target: str = "viewed"  # "viewed", "self", or "bulk"
    export_bulk_user_ids: list[str] = []  # For bulk export
    import_file_content: str = ""  # Uploaded JSON content
    import_preview_data: dict = {}  # Parsed import data for preview
    import_validation_errors: list[str] = []  # Validation errors to show user
    
    # Cached current values for performance (computed from history)
    # Structure: {user_id: {date: value}}
    _comments_cache: dict[str, dict[str, str]] = {}
    _flags_cache: dict[str, dict[str, str]] = {}
    _hours_cache: dict[str, dict[str, float]] = {}
    _flag_colors_cache: dict[str, dict[str, str]] = {}
    
    FLAG_CHOICES = [
        ("", "(blank)"),
        ("offered vacation client closed", "offered vacation client closed"),
        ("national day off", "national day off"),
        ("Akkodis offered day off", "Akkodis offered day off"),
        ("on vacation", "on vacation"),
        ("on vacation client closed", "on vacation client closed"),
        ("regional day off", "regional day off"),
        ("extra day off", "extra day off")
    ]
    
    FLAG_COLORS = {
        "offered vacation client closed": "#e53e3e",    # Red
        "national day off": "#dd6b20",   # Orange
        "Akkodis offered day off": "#3182ce",                        # Blue
        "on vacation": "#805ad5",                          # Purple
        "on vacation client closed": "#2f855a",                          # Green
        "regional day off": "#d53f8c",                          # Pink
        "extra day off": "#718096",                   # Gray
        "": "var(--white)",
    }
    
    @rx.var
    def comments(self) -> dict[str, str]:
        """Computed property: viewed user's comments from history."""
        user_id = self.viewed_user_id
        if user_id in self._comments_cache:
            return self._comments_cache[user_id]
        return {}
    
    @rx.var
    def flags(self) -> dict[str, str]:
        """Computed property: viewed user's flags from history."""
        user_id = self.viewed_user_id
        if user_id in self._flags_cache:
            return self._flags_cache[user_id]
        return {}
    
    @rx.var
    def hours(self) -> dict[str, float]:
        """Computed property: viewed user's hours from history."""
        user_id = self.viewed_user_id
        if user_id in self._hours_cache:
            return self._hours_cache[user_id]
        return {}
    
    @rx.var
    def flag_colors_by_date(self) -> dict[str, str]:
        """Computed property: viewed user's flag colors from history."""
        user_id = self.viewed_user_id
        if user_id in self._flag_colors_cache:
            return self._flag_colors_cache[user_id]
        return {}
    
    @rx.var
    def history_entries_for_selected(self) -> list[dict]:
        """Get history entries for currently selected date from viewed user's calendar."""
        user_id = self.viewed_user_id
        if user_id in self.history and self.selected_date in self.history[user_id]:
            return self.history[user_id][self.selected_date][::-1]
        return []
    
    @rx.var
    def comment_count(self) -> int:
        """Get the number of comments for viewed user."""
        user_id = self.viewed_user_id
        if user_id in self._comments_cache:
            return len(self._comments_cache[user_id])
        return 0
    
    @rx.var
    def viewed_calendar_status(self) -> str:
        """Get the validation status of the currently viewed calendar."""
        user_id = self.viewed_user_id
        # Initialize if not exists
        if user_id not in self.calendar_status:
            self.calendar_status[user_id] = self.STATUS_DRAFT
        return self.calendar_status[user_id]
    
    @rx.var
    def viewed_calendar_is_validated(self) -> bool:
        """Check if viewed calendar is in validated (live) status."""
        return self.viewed_calendar_status == self.STATUS_VALIDATED
    
    @rx.var
    def can_employee_view_own_calendar(self) -> bool:
        """Check if employee can view their own calendar (only if validated)."""
        if self.current_user_role != "employee":
            return True  # Managers and HR always see calendars
        if self.viewed_user_id != self.current_user_id:
            return False  # Employees can't view others
        return self.viewed_calendar_is_validated  # Can only see own if validated
    
    @rx.var
    def status_history_for_viewed(self) -> list[dict]:
        """Get status change history for viewed user's calendar."""
        user_id = self.viewed_user_id
        if user_id in self.status_history:
            return self.status_history[user_id][::-1]  # Newest first
        return []
    
    @rx.var
    def current_user(self) -> dict:
        """Get current user object."""
        for user in self.USERS:
            if user["id"] == self.current_user_id:
                return user
        return self.USERS[0]  # Default to first employee
    
    @rx.var
    def current_user_role(self) -> str:
        """Get current user's role."""
        return self.current_user["role"]
    
    @rx.var
    def current_user_name(self) -> str:
        """Get current user's name."""
        return self.current_user["name"]
    
    @rx.var
    def current_user_project(self) -> dict:
        """Get current user's project object."""
        project_id = self.current_user.get("project_id", "")
        for project in self.PROJECTS:
            if project["id"] == project_id:
                return project
        return self.PROJECTS[0]  # Default to first project
    
    @rx.var
    def current_project_name(self) -> str:
        """Get current user's project name."""
        return self.current_user_project["name"]
    
    @rx.var
    def visible_users(self) -> list[dict]:
        """Get users whose calendars are visible to current user.
        
        Rules:
        - Employees: see only themselves (if calendar is validated)
        - Managers: see all users in their project
        - HR: see all users (cross-project)
        
        Also initializes calendar status to draft if not exists.
        """
        role = self.current_user_role
        current_project_id = self.current_user.get("project_id", "")
        
        # Initialize all user calendar statuses to draft if not exists
        for user in self.USERS:
            uid = user["id"]
            if uid not in self.calendar_status:
                self.calendar_status[uid] = self.STATUS_DRAFT
            if uid not in self.status_history:
                self.status_history[uid] = []
        
        if role == "hr":
            # HR sees everyone
            return self.USERS
        elif role == "manager":
            # Managers see all users in their project
            return [u for u in self.USERS if u.get("project_id") == current_project_id]
        else:
            # Employees see only themselves
            return [self.current_user]
    
    @rx.var
    def users_grouped_by_project(self) -> list[tuple[str, list[tuple[str, list[dict]]]]]:
        """Get visible users grouped by project and then by region.
        Returns list of (project_name, [(region_name, [users])]) tuples.
        Structure: Project → Region → Users (all sorted alphabetically).
        """
        visible = self.visible_users
        
        # Group by project first
        projects_dict = {}
        for user in visible:
            project_id = user.get("project_id", "")
            # Find project name
            project_name = "Unknown"
            for proj in self.PROJECTS:
                if proj["id"] == project_id:
                    project_name = proj["name"]
                    break
            
            if project_name not in projects_dict:
                projects_dict[project_name] = []
            projects_dict[project_name].append(user)
        
        # Now group users within each project by region
        result = []
        for project_name in sorted(projects_dict.keys()):
            users_in_project = projects_dict[project_name]
            
            # Group by region
            regions_dict = {}
            for user in users_in_project:
                region = user.get("region", "Unknown")
                if region not in regions_dict:
                    regions_dict[region] = []
                regions_dict[region].append(user)
            
            # Sort users within each region by name
            for region in regions_dict:
                regions_dict[region].sort(key=lambda u: u.get("name", ""))
            
            # Convert to sorted list of (region, users) tuples
            regions_list = sorted(regions_dict.items())
            result.append((project_name, regions_list))
        
        return result
    
    @rx.var
    def can_edit_viewed_calendar(self) -> bool:
        """Check if current user can edit the calendar they're viewing.
        
        Rules:
        - Can always edit own calendar
        - Managers: read-only for team calendars
        - HR: can edit any calendar
        """
        if self.viewed_user_id == self.current_user_id:
            return True  # Can always edit own calendar
        
        if self.current_user_role == "hr":
            return True  # HR can edit any calendar
        
        return False  # Managers and employees cannot edit others' calendars
    
    @rx.var
    def viewed_user_name(self) -> str:
        """Get the name of the user whose calendar is being viewed."""
        for user in self.USERS:
            if user["id"] == self.viewed_user_id:
                return user["name"]
        return "Unknown"
    
    @rx.var
    def viewed_user_project_name(self) -> str:
        """Get the project name of the user whose calendar is being viewed."""
        for user in self.USERS:
            if user["id"] == self.viewed_user_id:
                project_id = user.get("project_id", "")
                for proj in self.PROJECTS:
                    if proj["id"] == project_id:
                        return proj["name"]
        return "Unknown"
    
    @rx.var
    def allowed_flags(self) -> list[tuple[str, str]]:
        """Get flags allowed for current user role."""
        role = self.current_user_role
        
        allowed = [("", "(blank)")]  # Everyone can use blank
        
        if role == "hr":
            # HR can set all flags
            for flag_key, flag_label in self.FLAG_CHOICES:
                if flag_key != "":
                    allowed.append((flag_key, flag_label))
        elif role == "manager":
            # Managers can set HR_MANAGER_FLAGS
            for flag_key, flag_label in self.FLAG_CHOICES:
                if flag_key in self.HR_MANAGER_FLAGS:
                    allowed.append((flag_key, flag_label))
        else:  # employee
            # Employees can only set EMPLOYEE_FLAGS
            for flag_key, flag_label in self.FLAG_CHOICES:
                if flag_key in self.EMPLOYEE_FLAGS:
                    allowed.append((flag_key, flag_label))
        
        return allowed
    
    @rx.var
    def range_display_text(self) -> str:
        """Get display text for range selection."""
        if self.range_start_date and self.range_end_date:
            if self.range_start_date == self.range_end_date:
                return self.range_start_date
            return f"{self.range_start_date} to {self.range_end_date}"
        elif self.range_start_date:
            return f"Start: {self.range_start_date} (click end date)"
        return "No date selected"
    
    @rx.var
    def is_range_selection(self) -> bool:
        """Check if currently selecting a range."""
        return self.range_start_date != "" and self.range_end_date == ""
    
    def is_weekday(self, date_str: str) -> bool:
        """Check if a date is a weekday (Monday-Friday)."""
        try:
            date_obj = datetime.strptime(date_str, "%a %b %d %Y")
            # Monday is 0, Sunday is 6
            return date_obj.weekday() < 5
        except ValueError:
            return False
    
    def switch_user(self, user_id: str):
        """Switch to a different user (changes who is logged in)."""
        self.current_user_id = user_id
        self.viewed_user_id = user_id  # Also view their calendar by default
        self.show_user_selector = False
        return rx.toast.success(
            f"Switched to {self.current_user_name}",
            position="top-center"
        )
    
    def view_user_calendar(self, user_id: str):
        """View a specific user's calendar (Manager/HR viewing team calendars)."""
        # Check if current user has permission to view this calendar
        visible_user_ids = [u["id"] for u in self.visible_users]
        if user_id not in visible_user_ids:
            return rx.toast.error(
                "Access Denied: You don't have permission to view this calendar",
                position="top-center",
                duration=5000
            )
        
        self.viewed_user_id = user_id
        
        # Get viewed user name
        viewed_user_name = "Unknown"
        for user in self.USERS:
            if user["id"] == user_id:
                viewed_user_name = user["name"]
                break
        
        # Different message if viewing own vs other's calendar
        if user_id == self.current_user_id:
            return rx.toast.info(
                f"Viewing your calendar",
                position="top-center"
            )
        else:
            return rx.toast.info(
                f"Viewing {viewed_user_name}'s calendar (read-only)" if self.current_user_role == "manager" else f"Viewing {viewed_user_name}'s calendar",
                position="top-center"
            )
    
    def toggle_user_selector(self):
        """Toggle user selector dialog."""
        self.show_user_selector = not self.show_user_selector
    
    def can_modify_flag(self, flag: str) -> bool:
        """Check if current user can modify a specific flag."""
        if flag == "":
            return True
        
        role = self.current_user_role
        
        if role == "hr":
            return True
        elif role == "manager":
            return flag in self.HR_MANAGER_FLAGS
        else:  # employee
            return flag in self.EMPLOYEE_FLAGS
    
    def can_edit_date(self, date_iso: str) -> bool:
        """Check if current user can edit a specific date in the viewed user's calendar."""
        target_user_id = self.viewed_user_id
        existing_flag = ""
        if target_user_id in self._flags_cache and date_iso in self._flags_cache[target_user_id]:
            existing_flag = self._flags_cache[target_user_id][date_iso]
        # If no flag or blank, anyone can edit
        if not existing_flag:
            return True
        # If HR-only flag and user is not HR, deny access
        if existing_flag in self.HR_ONLY_FLAGS and self.current_user_role != "hr":
            return False
        return True
    
    def get_weekdays_in_range(self, start_date: str, end_date: str) -> list[str]:
        """Get all weekdays between start and end date (inclusive)."""
        from datetime import timedelta
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        weekdays = []
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday to Friday
                weekdays.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return weekdays
    
    def handle_day_click(self, day_str: str):
        """Handle when a day is clicked on the calendar (supports range selection)."""
        # Check if current user can edit the viewed calendar
        if not self.can_edit_viewed_calendar:
            return rx.toast.error(
                f"Access Denied: You can only view {self.viewed_user_name}'s calendar (read-only)",
                position="top-center",
                duration=5000
            )
        
        # Check if it's a weekday
        if not self.is_weekday(day_str):
            return rx.toast.error(
                "Comments can only be added to weekdays (Monday-Friday)",
                position="top-center"
            )
        
        # Convert to YYYY-MM-DD format for storage
        date_obj = datetime.strptime(day_str, "%a %b %d %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        
        # Range selection logic
        user_id = self.viewed_user_id  # Write to viewed user's calendar (with permission check above)
        
        if not self.range_start_date:
            # First click: set start date
            # Check if this single date has HR-only protection
            if not self.can_edit_date(formatted_date):
                existing_flag = ""
                if user_id in self._flags_cache and formatted_date in self._flags_cache[user_id]:
                    existing_flag = self._flags_cache[user_id][formatted_date]
                return rx.toast.error(
                    f"Access Denied: Only HR can modify days with '{existing_flag}' flag",
                    position="top-center",
                    duration=5000
                )
            
            self.range_start_date = formatted_date
            self.is_selecting_range = True
            return rx.toast.info(
                f"Range Start: {date_obj.strftime('%B %d, %Y')} - Click another day to complete range",
                position="top-center"
            )
        else:
            # Second click: set end date
            # Validate end date is not before start date
            start_dt = datetime.strptime(self.range_start_date, "%Y-%m-%d")
            end_dt = date_obj
            
            if end_dt < start_dt:
                return rx.toast.error(
                    "End date cannot be before start date. Click again to select a valid end date.",
                    position="top-center",
                    duration=5000
                )
            
            self.range_end_date = formatted_date
            self.selected_date = f"{self.range_start_date} to {self.range_end_date}"
            self.is_selecting_range = False
            
            # Load values from user's calendar (for single day or first day in range)
            self.current_comment = ""
            self.current_flag = ""
            self.current_hours = 0.0
            
            if user_id in self._comments_cache:
                self.current_comment = self._comments_cache[user_id].get(self.range_start_date, "")
            if user_id in self._flags_cache:
                self.current_flag = self._flags_cache[user_id].get(self.range_start_date, "")
            if user_id in self._hours_cache:
                self.current_hours = float(self._hours_cache[user_id].get(self.range_start_date, 0.0))
            
            self.show_comment_dialog = True
            
            # Calculate weekdays in range
            weekdays = self.get_weekdays_in_range(self.range_start_date, self.range_end_date)
            
            return rx.toast.info(
                f"Range Selected: {len(weekdays)} weekday(s)",
                position="top-center"
            )
    
    def reset_range_selection(self):
        """Reset range selection state."""
        self.range_start_date = ""
        self.range_end_date = ""
        self.is_selecting_range = False
        self.hovered_date = ""
    
    def set_hovered_date(self, date_str: str):
        """Set the currently hovered date for visual feedback."""
        if date_str and self.is_selecting_range:
            try:
                date_obj = datetime.strptime(date_str, "%a %b %d %Y")
                self.hovered_date = date_obj.strftime("%Y-%m-%d")
            except:
                self.hovered_date = ""
        else:
            self.hovered_date = ""
    
    def save_comment(self):
        """Save the current comment/flag/hours to range or single date (append-only)."""
        if not self.range_start_date:
            return
        
        # Prepare values
        comment = self.current_comment.strip()
        flag = self.current_flag
        hours = 0.0 if flag else max(0.0, min(12.0, round(float(self.current_hours) * 2) / 2.0))
        
        # Check if user has permission to set this flag
        if not self.can_modify_flag(flag):
            role_name = {"employee": "Employees", "manager": "Managers", "hr": "HR Services"}[self.current_user_role]
            return rx.toast.error(
                f"Access Denied: {role_name} cannot set '{flag}' flag",
                position="top-center",
                duration=5000
            )
        
        # Get all weekdays in range (or single day if end date not set or same as start)
        if self.range_end_date and self.range_end_date != self.range_start_date:
            target_dates = self.get_weekdays_in_range(self.range_start_date, self.range_end_date)
        else:
            target_dates = [self.range_start_date]
        
        # Filter out HR-protected dates (skip them with warning)
        allowed_dates = []
        protected_dates = []
        
        for date_iso in target_dates:
            if self.can_edit_date(date_iso):
                allowed_dates.append(date_iso)
            else:
                protected_dates.append(date_iso)
        
        # If no dates can be modified, show error
        if not allowed_dates:
            return rx.toast.error(
                f"Access Denied: All selected dates are HR-protected. Only HR can modify these dates.",
                position="top-center",
                duration=5000
            )
        
        # HR-only flag propagation: if HR sets an HR-only flag, apply company-wide or region-wide
        if self.current_user_role == "hr" and flag in self.HR_ONLY_FLAGS:
            # For regional day off, check if region is selected
            if flag == "regional day off" and not self.selected_region:
                return rx.toast.error(
                    "Please select a region for the regional day off",
                    position="top-center",
                    duration=5000
                )
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Ensure notifications structure
            for u in self.USERS:
                if u["id"] not in self.notifications:
                    self.notifications[u["id"]] = []
            
            # Determine target users based on flag type
            target_users = []
            scope_description = ""
            
            if flag == "regional day off":
                # Only users in the selected region
                target_users = [u for u in self.USERS if u.get("region") == self.selected_region]
                scope_description = f"region {self.selected_region}"
            else:
                # National day off or Akkodis offered day off: all users
                target_users = self.USERS
                scope_description = "company-wide"
            
            total_dates = 0
            for date_iso in allowed_dates:
                # Only propagate within calendar year 2026
                try:
                    if int(date_iso[:4]) != 2026:
                        continue
                except Exception:
                    continue
                self.company_holidays[date_iso] = flag  # Record company holiday
                for user in target_users:
                    uid = user["id"]
                    # Init user structures
                    if uid not in self.history:
                        self.history[uid] = {}
                    if uid not in self._comments_cache:
                        self._comments_cache[uid] = {}
                    if uid not in self._flags_cache:
                        self._flags_cache[uid] = {}
                    if uid not in self._hours_cache:
                        self._hours_cache[uid] = {}
                    if uid not in self._flag_colors_cache:
                        self._flag_colors_cache[uid] = {}
                    prev_comment = self._comments_cache[uid].get(date_iso, "")
                    prev_flag = self._flags_cache[uid].get(date_iso, "")
                    prev_hours = self._hours_cache[uid].get(date_iso, 0.0)
                    new_comment = comment  # Overwrite comment company-wide (Option A)
                    new_flag = flag
                    new_hours = 0.0
                    actions = []
                    if new_comment != prev_comment:
                        actions.append("comment modified" if prev_comment else "comment added")
                    if new_flag != prev_flag:
                        actions.append("flag changed")
                    if new_hours != prev_hours:
                        actions.append("hours changed")
                    if not actions:
                        actions.append("holiday set")
                    
                    # Build action description
                    action_desc = ", ".join(actions)
                    if flag == "regional day off":
                        action_desc += f" ({self.selected_region} region)"
                    else:
                        action_desc += " (company-wide)"
                    
                    entry = {
                        "timestamp": timestamp,
                        "action": action_desc,
                        "comment": new_comment,
                        "flag": new_flag,
                        "hours": new_hours,
                        "user": self.current_user_name,
                        "user_role": self.current_user_role,
                        "propagated_by": self.current_user_name,
                    }
                    if date_iso not in self.history[uid]:
                        self.history[uid][date_iso] = []
                    self.history[uid][date_iso].append(entry)
                    self._comments_cache[uid][date_iso] = new_comment
                    self._flags_cache[uid][date_iso] = new_flag
                    self._hours_cache[uid][date_iso] = new_hours
                    self._flag_colors_cache[uid][date_iso] = self.FLAG_COLORS.get(new_flag, "transparent")
                    
                    # Notification (memo) for user with region info
                    if flag == "regional day off":
                        notif = f"Regional holiday for {self.selected_region} - '{new_flag}' added on {date_iso} by {self.current_user_name} (HR)."
                    else:
                        notif = f"Company holiday '{new_flag}' added on {date_iso} by {self.current_user_name} (HR)."
                    self.notifications[uid].append(notif)
                total_dates += 1
            
            # Close dialog, reset, toast
            self.close_comment_dialog()
            self.reset_range_selection()
            return rx.toast.success(
                f"Holiday applied to {total_dates} date(s) across {len(target_users)} calendars ({scope_description}).",
                position="top-center",
                duration=6000
            )

        # Local (non-propagating) update
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        saved_count = 0
        user_id = self.viewed_user_id
        
        # Initialize user history and caches if needed
        if user_id not in self.history:
            self.history[user_id] = {}
        if user_id not in self._comments_cache:
            self._comments_cache[user_id] = {}
        if user_id not in self._flags_cache:
            self._flags_cache[user_id] = {}
        if user_id not in self._hours_cache:
            self._hours_cache[user_id] = {}
        if user_id not in self._flag_colors_cache:
            self._flag_colors_cache[user_id] = {}
        
        for date_iso in allowed_dates:
            # Get previous values to determine action
            prev_comment = self._comments_cache[user_id].get(date_iso, "")
            prev_flag = self._flags_cache[user_id].get(date_iso, "")
            prev_hours = self._hours_cache[user_id].get(date_iso, 0.0)
            
            # Determine action description
            actions = []
            if comment != prev_comment:
                actions.append("comment modified" if prev_comment else "comment added")
            if flag != prev_flag:
                actions.append("flag changed")
            if hours != prev_hours and not flag:
                actions.append("hours changed")
            
            action = ", ".join(actions) if actions else "no changes"
            
            # Create history entry with user info
            entry = {
                "timestamp": timestamp,
                "action": action,
                "comment": comment,
                "flag": flag,
                "hours": hours,
                "user": self.current_user_name,
                "user_role": self.current_user_role
            }
            
            # Append to user's history
            if date_iso not in self.history[user_id]:
                self.history[user_id][date_iso] = []
            self.history[user_id][date_iso].append(entry)
            
            # Update user's caches
            self._comments_cache[user_id][date_iso] = comment
            self._flags_cache[user_id][date_iso] = flag
            self._hours_cache[user_id][date_iso] = hours
            if flag:
                self._flag_colors_cache[user_id][date_iso] = self.FLAG_COLORS.get(flag, "transparent")
            elif date_iso in self._flag_colors_cache[user_id]:
                del self._flag_colors_cache[user_id][date_iso]
            
            saved_count += 1
        
        # Calendar validation status update: HR modification triggers status change
        if self.current_user_role == "hr" and user_id != self.current_user_id:
            # HR is modifying someone else's calendar
            viewed_user = next((u for u in self.USERS if u["id"] == user_id), None)
            if viewed_user:
                viewed_role = viewed_user.get("role", "")
                # Only trigger status change for employee/manager calendars (not HR)
                if viewed_role in ["employee", "manager"]:
                    old_status = self.calendar_status.get(user_id, self.STATUS_DRAFT)
                    # Auto-revert to pending_manager_validation
                    if old_status != self.STATUS_PENDING_MANAGER:
                        self.calendar_status[user_id] = self.STATUS_PENDING_MANAGER
                        changes_desc = f"HR modified {saved_count} date(s): {action}"
                        self._log_status_change(user_id, old_status, self.STATUS_PENDING_MANAGER, changes_desc)
        
        self.close_comment_dialog()
        self.reset_range_selection()
        
        # Show success message with warning if some dates were protected
        if protected_dates:
            return rx.toast.warning(
                f"Saved {saved_count} date(s). Skipped {len(protected_dates)} HR-protected date(s) by {self.current_user_name}",
                position="top-center",
                duration=5000
            )
        else:
            return rx.toast.success(
                f"Saved {saved_count} date(s) by {self.current_user_name}",
                position="top-center",
                duration=4000
            )

    # Company holidays bulk dialog controls
    def open_company_holidays_dialog(self):
        self.show_company_holidays_dialog = True

    def close_company_holidays_dialog(self):
        self.show_company_holidays_dialog = False

    @rx.var
    def company_holidays_list(self) -> list[tuple[str, str]]:
        """Sorted list of (date, flag) for company holidays."""
        return sorted(self.company_holidays.items())

    @rx.var
    def notifications_for_viewed(self) -> list[str]:
        uid = self.viewed_user_id
        if uid in self.notifications:
            return self.notifications[uid]
        return []

    def dismiss_notifications_for_viewed(self):
        uid = self.viewed_user_id
        if uid in self.notifications:
            self.notifications[uid] = []
    
    def set_current_comment(self, value: str):
        """Set the current comment."""
        self.current_comment = value

    def set_current_flag(self, value: str):
        """Set the current flag in the dialog.

        If a non-blank flag is selected, enforce hours to 0.
        """
        self.current_flag = value
        if value:
            # enforce 0 hours when a flag is chosen
            self.current_hours = 0.0

    def set_current_hours(self, value: str):
        """Set the hours value."""
        try:
            self.current_hours = float(value)
        except ValueError:
            self.current_hours = 0.0
    
    def set_selected_region(self, region: str):
        """Set the selected region for regional day off (HR only)."""
        self.selected_region = region
    
    def close_comment_dialog(self):
        """Close the comment dialog and reset range selection."""
        self.show_comment_dialog = False
        self.current_comment = ""
        self.selected_date = ""
        self.selected_region = ""  # Reset region selection
        self.reset_range_selection()
    
    def open_history_dialog(self):
        """Open the history dialog for the selected date."""
        self.show_history_dialog = True
    
    def close_history_dialog(self):
        """Close the history dialog."""
        self.show_history_dialog = False

    # Calendar validation status methods
    def _log_status_change(self, user_id: str, from_status: str, to_status: str, changes_summary: str = ""):
        """Internal method to log status changes with full audit info."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "from_status": from_status,
            "to_status": to_status,
            "actor": self.current_user_name,
            "actor_role": self.current_user_role,
            "changes_summary": changes_summary
        }
        
        if user_id not in self.status_history:
            self.status_history[user_id] = []
        self.status_history[user_id].append(entry)
    
    def open_hr_self_validate_dialog(self):
        """Open confirmation dialog for HR to validate their own calendar."""
        if self.current_user_role != "hr":
            return rx.toast.error("Only HR can use this feature", position="top-center")
        if self.viewed_user_id != self.current_user_id:
            return rx.toast.error("You can only self-validate your own calendar", position="top-center")
        self.show_hr_self_validate_dialog = True
    
    def close_hr_self_validate_dialog(self):
        """Close HR self-validate dialog."""
        self.show_hr_self_validate_dialog = False
    
    def hr_self_validate_calendar(self):
        """HR validates their own calendar directly (no manager review needed)."""
        user_id = self.current_user_id
        old_status = self.calendar_status.get(user_id, self.STATUS_DRAFT)
        
        self.calendar_status[user_id] = self.STATUS_VALIDATED
        self._log_status_change(user_id, old_status, self.STATUS_VALIDATED, "HR self-validated calendar")
        
        self.close_hr_self_validate_dialog()
        return rx.toast.success(
            "Your calendar has been validated and is now live",
            position="top-center",
            duration=5000
        )
    
    def open_manager_validate_dialog(self):
        """Open confirmation dialog for manager to validate a calendar."""
        if self.current_user_role != "manager":
            return rx.toast.error("Only managers can validate calendars", position="top-center")
        
        viewed_user = next((u for u in self.USERS if u["id"] == self.viewed_user_id), None)
        if not viewed_user:
            return rx.toast.error("User not found", position="top-center")
        
        # Can't validate own calendar through this flow (they view it normally)
        if self.viewed_user_id == self.current_user_id:
            return rx.toast.error("Use regular workflow to manage your own calendar", position="top-center")
        
        self.show_manager_validate_dialog = True
    
    def close_manager_validate_dialog(self):
        """Close manager validate dialog."""
        self.show_manager_validate_dialog = False
    
    def manager_validate_calendar(self):
        """Manager validates a calendar and sends it back to HR with status validated_by_manager."""
        user_id = self.viewed_user_id
        old_status = self.calendar_status.get(user_id, self.STATUS_DRAFT)
        
        self.calendar_status[user_id] = self.STATUS_VALIDATED_BY_MANAGER
        self._log_status_change(
            user_id, 
            old_status, 
            self.STATUS_VALIDATED_BY_MANAGER, 
            f"Manager validated calendar for {self.viewed_user_name}"
        )
        
        self.close_manager_validate_dialog()
        return rx.toast.success(
            f"Calendar validated and sent to HR for final approval",
            position="top-center",
            duration=5000
        )
    
    def open_hr_final_validate_dialog(self):
        """Open confirmation dialog for HR to finalize calendar validation."""
        if self.current_user_role != "hr":
            return rx.toast.error("Only HR can finalize validation", position="top-center")
        
        # Check if calendar is in validated_by_manager status
        current_status = self.calendar_status.get(self.viewed_user_id, self.STATUS_DRAFT)
        if current_status != self.STATUS_VALIDATED_BY_MANAGER:
            return rx.toast.error(
                f"Calendar must be validated by manager first. Current status: {current_status}",
                position="top-center",
                duration=5000
            )
        
        self.show_hr_final_validate_dialog = True
    
    def close_hr_final_validate_dialog(self):
        """Close HR final validate dialog."""
        self.show_hr_final_validate_dialog = False
    
    def hr_final_validate_calendar(self):
        """HR performs final validation, making the calendar live."""
        user_id = self.viewed_user_id
        old_status = self.calendar_status.get(user_id, self.STATUS_DRAFT)
        
        self.calendar_status[user_id] = self.STATUS_VALIDATED
        self._log_status_change(
            user_id,
            old_status,
            self.STATUS_VALIDATED,
            f"HR finalized validation for {self.viewed_user_name}"
        )
        
        self.close_hr_final_validate_dialog()
        return rx.toast.success(
            f"Calendar for {self.viewed_user_name} is now validated and live!",
            position="top-center",
            duration=5000
        )
    
    def open_status_history_dialog(self):
        """Open status history dialog."""
        self.show_status_history_dialog = True
    
    def close_status_history_dialog(self):
        """Close status history dialog."""
        self.show_status_history_dialog = False

    # Bulk hours methods
    def open_bulk_hours_dialog(self, month: int):
        """Open the bulk hours dialog for a specific month."""
        # Only managers and HR can use this feature
        if self.current_user_role == "employee":
            return rx.toast.error(
                "Access Denied: Only managers and HR can bulk-set hours",
                position="top-center",
                duration=5000
            )
        
        self.selected_month = month
        self.bulk_hours_mon_thu = 8.0
        self.bulk_hours_fri = 8.0
        self.show_bulk_hours_dialog = True
    
    def close_bulk_hours_dialog(self):
        """Close the bulk hours dialog."""
        self.show_bulk_hours_dialog = False
        self.show_bulk_hours_confirmation = False
        self.bulk_affected_days_count = 0
        self.bulk_overwrite_count = 0
    
    def set_bulk_hours_mon_thu(self, value: str):
        """Set bulk hours for Monday-Thursday."""
        try:
            hours = float(value)
            # Validate range 6.0 to 19.0
            self.bulk_hours_mon_thu = max(6.0, min(19.0, hours))
        except ValueError:
            self.bulk_hours_mon_thu = 8.0
    
    def set_bulk_hours_fri(self, value: str):
        """Set bulk hours for Friday."""
        try:
            hours = float(value)
            # Validate range 6.0 to 19.0
            self.bulk_hours_fri = max(6.0, min(19.0, hours))
        except ValueError:
            self.bulk_hours_fri = 6.0

    def get_flag_for_date(self, date_iso: str) -> str:
        """Get flag for a date from viewed user's calendar."""
        user_id = self.viewed_user_id
        if user_id in self._flags_cache:
            return self._flags_cache[user_id].get(date_iso, "")
        return ""

    def get_hours_for_date(self, date_iso: str) -> float:
        """Get hours for a date from viewed user's calendar."""
        user_id = self.viewed_user_id
        if user_id in self._hours_cache:
            return float(self._hours_cache[user_id].get(date_iso, 0.0))
        return 0.0
    
    def preview_bulk_hours(self):
        """Preview how many days will be affected by bulk hours setting."""
        from datetime import timedelta
        
        # Get all weekdays in the selected month for year 2026
        year = 2026
        month = self.selected_month
        
        # Get first and last day of month
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Get all weekdays
        weekdays = []
        current = first_day
        while current <= last_day:
            if current.weekday() < 5:  # Monday to Friday
                weekdays.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        # Get all visible users
        target_users = self.visible_users
        
        # Count affected days and days with existing hours
        affected_count = 0
        overwrite_count = 0
        
        for user in target_users:
            uid = user["id"]
            for date_iso in weekdays:
                # Check if date has a flag (skip if it does)
                has_flag = False
                if uid in self._flags_cache and date_iso in self._flags_cache[uid]:
                    if self._flags_cache[uid][date_iso]:
                        has_flag = True
                
                if not has_flag:
                    affected_count += 1
                    # Check if it already has hours
                    if uid in self._hours_cache and date_iso in self._hours_cache[uid]:
                        if self._hours_cache[uid][date_iso] > 0:
                            overwrite_count += 1
        
        self.bulk_affected_days_count = affected_count
        self.bulk_overwrite_count = overwrite_count
        
        # Show confirmation dialog if there are days to overwrite
        if overwrite_count > 0:
            self.show_bulk_hours_confirmation = True
        else:
            # No overwrites, proceed directly
            return self.apply_bulk_hours()
    
    def apply_bulk_hours(self):
        """Apply bulk hours to all visible users for the selected month."""
        from datetime import timedelta
        
        # Get all weekdays in the selected month
        year = 2026
        month = self.selected_month
        
        first_day = datetime(year, month, 1)
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)
        
        # Get all weekdays
        weekdays = []
        current = first_day
        while current <= last_day:
            if current.weekday() < 5:  # Monday to Friday
                weekdays.append((current.strftime("%Y-%m-%d"), current.weekday()))
            current += timedelta(days=1)
        
        # Get all visible users
        target_users = self.visible_users
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total_updated = 0
        
        for user in target_users:
            uid = user["id"]
            
            # Initialize structures if needed
            if uid not in self.history:
                self.history[uid] = {}
            if uid not in self._hours_cache:
                self._hours_cache[uid] = {}
            if uid not in self._flags_cache:
                self._flags_cache[uid] = {}
            if uid not in self._comments_cache:
                self._comments_cache[uid] = {}
            if uid not in self._flag_colors_cache:
                self._flag_colors_cache[uid] = {}
            
            for date_iso, weekday in weekdays:
                # Skip if date has a flag
                existing_flag = self._flags_cache[uid].get(date_iso, "")
                if existing_flag:
                    continue  # Skip dates with flags
                
                # Determine hours based on day of week
                # weekday: 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday
                if weekday < 4:  # Monday to Thursday
                    hours = self.bulk_hours_mon_thu
                else:  # Friday
                    hours = self.bulk_hours_fri
                
                # Get previous values
                prev_comment = self._comments_cache[uid].get(date_iso, "")
                prev_hours = self._hours_cache[uid].get(date_iso, 0.0)
                
                # Skip if no change
                if prev_hours == hours:
                    continue
                
                # Create history entry
                action = "hours changed (bulk set)" if prev_hours > 0 else "hours added (bulk set)"
                entry = {
                    "timestamp": timestamp,
                    "action": action,
                    "comment": prev_comment,
                    "flag": "",
                    "hours": hours,
                    "user": self.current_user_name,
                    "user_role": self.current_user_role
                }
                
                # Update history
                if date_iso not in self.history[uid]:
                    self.history[uid][date_iso] = []
                self.history[uid][date_iso].append(entry)
                
                # Update cache
                self._hours_cache[uid][date_iso] = hours
                total_updated += 1
            
            # Calendar validation status update: HR bulk hours triggers status change
            if self.current_user_role == "hr" and uid != self.current_user_id:
                # HR is bulk-setting hours for someone else's calendar
                target_user = next((u for u in self.USERS if u["id"] == uid), None)
                if target_user:
                    target_role = target_user.get("role", "")
                    # Only trigger status change for employee/manager calendars
                    if target_role in ["employee", "manager"]:
                        old_status = self.calendar_status.get(uid, self.STATUS_DRAFT)
                        # Auto-revert to pending_manager_validation
                        if old_status != self.STATUS_PENDING_MANAGER:
                            self.calendar_status[uid] = self.STATUS_PENDING_MANAGER
                            changes_desc = f"HR bulk-set hours for month {month}"
                            self._log_status_change(uid, old_status, self.STATUS_PENDING_MANAGER, changes_desc)
        
        # Close dialogs
        self.close_bulk_hours_dialog()
        
        # Success message
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return rx.toast.success(
            f"Bulk hours set for {month_names[month - 1]}: {total_updated} day(s) updated across {len(target_users)} user(s)",
            position="top-center",
            duration=6000
        )
    
    def export_to_json(self):
        """Export the current user's calendar with full history to a JSON file."""
        user_id = self.current_user_id
        
        # Prepare data with readable format including full history
        export_data = {
            "year": 2026,
            "user": self.current_user_name,
            "project": self.current_project_name,
            "entries": []
        }
        
        # Check if user has history
        if user_id not in self.history:
            return rx.download(data=json.dumps(export_data, indent=2), filename=f"calendar_export_{user_id}.json")
        
        # Sort by date
        sorted_dates = sorted(self.history[user_id].keys())
        for date_str in sorted_dates:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            
            # Get current values from cache
            entry = {
                "date": date_str,
                "day_name": date_obj.strftime("%A"),
                "formatted_date": date_obj.strftime("%B %d, %Y"),
                "current": {
                    "comment": self._comments_cache[user_id].get(date_str, ""),
                    "flag": self._flags_cache[user_id].get(date_str, ""),
                    "hours": self._hours_cache[user_id].get(date_str, 0.0)
                },
                "history": self.history[user_id][date_str]
            }
            
            export_data["entries"].append(entry)
        
        # Create JSON string
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # Return download event
        return rx.download(
            data=json_str,
            filename="calendar_2026_data.json"
        )
    
    def get_comment_for_date(self, month: int, day: int) -> str:
        """Get comment for a specific date from viewed user's calendar."""
        date_str = f"2026-{month:02d}-{day:02d}"
        user_id = self.viewed_user_id
        if user_id in self._comments_cache:
            return self._comments_cache[user_id].get(date_str, "")
        return ""
    
    def has_comment(self, month: int, day: int) -> bool:
        """Check if a date has a comment in viewed user's calendar."""
        date_str = f"2026-{month:02d}-{day:02d}"
        user_id = self.viewed_user_id
        if user_id in self._comments_cache:
            return date_str in self._comments_cache[user_id]
        return False

    def get_flag_color_for_legend(self, flag_key: str) -> str:
        """Get color for a specific flag (for legend)."""
        if flag_key == "":
            return "transparent"
        return self.FLAG_COLORS.get(flag_key, "transparent")
    
    def get_flag_label(self, flag_key: str) -> str:
        """Get label for a specific flag (for legend)."""
        for key, label in self.FLAG_CHOICES:
            if key == flag_key:
                return label
        return flag_key

    # Export/Import methods
    def open_export_dialog(self):
        """Open export dialog."""
        # Only HR and managers can export
        if self.current_user_role == "employee":
            return rx.toast.error(
                "Access Denied: Only managers and HR can export calendars",
                position="top-center",
                duration=5000
            )
        self.export_target = "viewed"
        self.export_bulk_user_ids = []
        self.show_export_dialog = True
    
    def close_export_dialog(self):
        """Close export dialog."""
        self.show_export_dialog = False
        self.export_target = "viewed"
        self.export_bulk_user_ids = []
    
    def set_export_target(self, target: str):
        """Set export target: viewed, self, or bulk."""
        self.export_target = target
        if target == "bulk":
            # Pre-select all visible users for bulk export
            self.export_bulk_user_ids = [u["id"] for u in self.visible_users]
    
    def toggle_bulk_export_user(self, user_id: str):
        """Toggle user selection for bulk export."""
        if user_id in self.export_bulk_user_ids:
            self.export_bulk_user_ids.remove(user_id)
        else:
            self.export_bulk_user_ids.append(user_id)
    
    def export_calendar(self) -> rx.event.EventSpec:
        """Export calendar(s) to JSON file(s)."""
        # Determine which users to export
        if self.export_target == "viewed":
            user_ids = [self.viewed_user_id]
        elif self.export_target == "self":
            user_ids = [self.current_user_id]
        elif self.export_target == "bulk":
            user_ids = self.export_bulk_user_ids
        else:
            user_ids = [self.viewed_user_id]
        
        if not user_ids:
            return rx.toast.error(
                "No users selected for export",
                position="top-center",
                duration=4000
            )
        
        # Export single or multiple calendars
        if len(user_ids) == 1:
            # Single calendar export
            export_data = self._generate_calendar_export(user_ids[0])
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            user = next((u for u in self.USERS if u["id"] == user_ids[0]), None)
            filename = f"calendar_{user['name'].replace(' ', '_')}_{user_ids[0]}.json" if user else "calendar_export.json"
            
            self.close_export_dialog()
            return rx.download(data=json_str, filename=filename)
        else:
            # Bulk export - create array of calendars
            export_data = {
                "export_metadata": {
                    "export_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "exporter": self.current_user_id,
                    "exporter_name": self.current_user_name,
                    "export_count": len(user_ids)
                },
                "calendars": [self._generate_calendar_export(uid) for uid in user_ids]
            }
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            self.close_export_dialog()
            return rx.download(data=json_str, filename=f"calendar_bulk_export_{len(user_ids)}_users.json")
    
    def _generate_calendar_export(self, user_id: str) -> dict:
        """Generate export data for a single user's calendar."""
        user = next((u for u in self.USERS if u["id"] == user_id), None)
        if not user:
            return {}
        
        # Find project
        project = next((p for p in self.PROJECTS if p["id"] == user.get("project_id")), None)
        
        # Build days array with all calendar data
        days = []
        for month in range(1, 13):
            for day in range(1, 32):
                try:
                    date_obj = datetime(2026, month, day)
                    date_iso = date_obj.strftime("%Y-%m-%d")
                    
                    # Get current values from cache
                    flag = self._flags_cache.get(user_id, {}).get(date_iso, "")
                    comment = self._comments_cache.get(user_id, {}).get(date_iso, "")
                    hours = self._hours_cache.get(user_id, {}).get(date_iso, 0.0)
                    
                    # Only include days with data
                    if flag or comment or hours > 0:
                        days.append({
                            "date": date_iso,
                            "flag": flag,
                            "comment": comment,
                            "hours": hours
                        })
                except ValueError:
                    # Invalid date (e.g., Feb 30)
                    continue
        
        return {
            "export_metadata": {
                "export_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "exporter": self.current_user_id,
                "exporter_name": self.current_user_name
            },
            "calendar_owner": {
                "id": user["id"],
                "name": user["name"],
                "role": user["role"]
            },
            "project": project if project else {"id": "", "name": "", "description": ""},
            "region": user.get("region", ""),
            "year": 2026,
            "calendar_status": self.calendar_status.get(user_id, self.STATUS_DRAFT),
            "days": days
        }
    
    def open_import_dialog(self):
        """Open import dialog."""
        # Only HR and managers can import
        if self.current_user_role == "employee":
            return rx.toast.error(
                "Access Denied: Only managers and HR can import calendars",
                position="top-center",
                duration=5000
            )
        self.import_file_content = ""
        self.import_preview_data = {}
        self.import_validation_errors = []
        self.show_import_dialog = True
    
    def close_import_dialog(self):
        """Close import dialog."""
        self.show_import_dialog = False
        self.show_import_confirmation_dialog = False
        self.import_file_content = ""
        self.import_preview_data = {}
        self.import_validation_errors = []
    
    async def handle_import_file_upload(self, files: list[rx.UploadFile]):
        """Handle uploaded JSON file for import."""
        if not files:
            return
        
        file = files[0]
        try:
            # Read file content
            content = await file.read()
            self.import_file_content = content.decode("utf-8")
            
            # Parse JSON
            import_data = json.loads(self.import_file_content)
            
            # Validate and preview
            self._validate_and_preview_import(import_data)
            
            if not self.import_validation_errors:
                self.show_import_confirmation_dialog = True
        except json.JSONDecodeError as e:
            self.import_validation_errors = [f"Invalid JSON format: {str(e)}"]
            return rx.toast.error(
                "Invalid JSON file",
                position="top-center",
                duration=4000
            )
        except Exception as e:
            self.import_validation_errors = [f"Error reading file: {str(e)}"]
            return rx.toast.error(
                "Error reading file",
                position="top-center",
                duration=4000
            )
    
    def _validate_and_preview_import(self, import_data: dict):
        """Validate import data and generate preview."""
        self.import_validation_errors = []
        self.import_preview_data = {}
        
        # Basic structure validation
        if "calendar_owner" not in import_data:
            self.import_validation_errors.append("Missing 'calendar_owner' field")
            return
        
        owner = import_data.get("calendar_owner", {})
        user_id = owner.get("id", "")
        user_name = owner.get("name", "")
        user_role = owner.get("role", "")
        
        if not user_id or not user_name or not user_role:
            self.import_validation_errors.append("Incomplete calendar_owner data")
            return
        
        # Check if user exists
        existing_user = next((u for u in self.USERS if u["id"] == user_id), None)
        is_new_user = existing_user is None
        
        # Permission check
        if self.current_user_role == "manager":
            # Managers can only import for their project
            if not is_new_user:
                if existing_user.get("project_id") != self.current_user.get("project_id"):
                    self.import_validation_errors.append(
                        "Managers can only import calendars for users in their project"
                    )
                    return
        
        # Get project and region info
        project_data = import_data.get("project", {})
        region = import_data.get("region", "")
        
        # Build preview
        self.import_preview_data = {
            "user_id": user_id,
            "user_name": user_name,
            "user_role": user_role,
            "is_new_user": is_new_user,
            "project": project_data,
            "region": region,
            "days_count": len(import_data.get("days", [])),
            "hr_flags_in_import": [],
            "non_hr_flags_in_import": [],
            "import_action": "create" if is_new_user else "update"
        }
        
        # Analyze flags
        days = import_data.get("days", [])
        for day in days:
            flag = day.get("flag", "")
            if flag in self.HR_ONLY_FLAGS:
                if flag not in self.import_preview_data["hr_flags_in_import"]:
                    self.import_preview_data["hr_flags_in_import"].append(flag)
            elif flag:
                if flag not in self.import_preview_data["non_hr_flags_in_import"]:
                    self.import_preview_data["non_hr_flags_in_import"].append(flag)
    
    def confirm_import_calendar(self):
        """Execute the calendar import after confirmation."""
        try:
            import_data = json.loads(self.import_file_content)
            result = self._execute_import(import_data)
            
            self.close_import_dialog()
            
            if result["success"]:
                return rx.toast.success(
                    result["message"],
                    position="top-center",
                    duration=6000
                )
            else:
                return rx.toast.error(
                    result["message"],
                    position="top-center",
                    duration=6000
                )
        except Exception as e:
            self.close_import_dialog()
            return rx.toast.error(
                f"Import failed: {str(e)}",
                position="top-center",
                duration=6000
            )
    
    def _execute_import(self, import_data: dict) -> dict:
        """Execute the actual import operation."""
        owner = import_data.get("calendar_owner", {})
        user_id = owner.get("id", "")
        user_name = owner.get("name", "")
        user_role = owner.get("role", "")
        
        project_data = import_data.get("project", {})
        region = import_data.get("region", "")
        
        # Check if user exists
        existing_user = next((u for u in self.USERS if u["id"] == user_id), None)
        is_new_user = existing_user is None
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if is_new_user:
            # NEW EMPLOYEE SCENARIO
            # 1. Add/reuse project
            project_id = project_data.get("id", "")
            existing_project = next((p for p in self.PROJECTS if p["id"] == project_id), None)
            
            if not existing_project and project_id:
                # Add new project
                new_project = {
                    "id": project_id,
                    "name": project_data.get("name", ""),
                    "description": project_data.get("description", "")
                }
                self.PROJECTS.append(new_project)
            
            # 2. Add/reuse region
            if region and region not in self.REGIONS:
                self.REGIONS.append(region)
            
            # 3. Add new user
            new_user = {
                "id": user_id,
                "name": user_name,
                "role": user_role,
                "project_id": project_id,
                "region": region
            }
            self.USERS.append(new_user)
            
            # 4. Initialize user data structures
            self.history[user_id] = {}
            self._comments_cache[user_id] = {}
            self._flags_cache[user_id] = {}
            self._hours_cache[user_id] = {}
            self._flag_colors_cache[user_id] = {}
            self.calendar_status[user_id] = self.STATUS_DRAFT
            self.status_history[user_id] = []
            
            # 5. Import all days from file
            days = import_data.get("days", [])
            for day in days:
                date_iso = day.get("date", "")
                flag = day.get("flag", "")
                comment = day.get("comment", "")
                hours = day.get("hours", 0.0)
                
                if not date_iso:
                    continue
                
                # Create history entry
                entry = {
                    "timestamp": timestamp,
                    "action": "imported",
                    "comment": comment,
                    "flag": flag,
                    "hours": hours,
                    "user": self.current_user_name,
                    "user_role": self.current_user_role
                }
                
                if date_iso not in self.history[user_id]:
                    self.history[user_id][date_iso] = []
                self.history[user_id][date_iso].append(entry)
                
                # Update caches
                self._comments_cache[user_id][date_iso] = comment
                self._flags_cache[user_id][date_iso] = flag
                self._hours_cache[user_id][date_iso] = hours
                if flag:
                    self._flag_colors_cache[user_id][date_iso] = self.FLAG_COLORS.get(flag, "transparent")
            
            # 6. Merge HR flags from existing project calendars
            if existing_project or project_id:
                # Find HR users in same project
                hr_users_in_project = [
                    u for u in self.USERS 
                    if u.get("project_id") == project_id 
                    and u.get("role") == "hr" 
                    and u["id"] != user_id
                ]
                
                # Copy HR flags from any HR user in the project
                for hr_user in hr_users_in_project:
                    hr_id = hr_user["id"]
                    if hr_id in self._flags_cache:
                        for date_iso, flag in self._flags_cache[hr_id].items():
                            # Copy HR-only flags
                            if flag in self.HR_ONLY_FLAGS:
                                # Only copy if new user doesn't have this flag yet
                                if date_iso not in self._flags_cache[user_id] or not self._flags_cache[user_id][date_iso]:
                                    # Special case: regional day off only if same region
                                    if flag == "regional day off" and hr_user.get("region") != region:
                                        continue
                                    
                                    # Copy the flag
                                    self._flags_cache[user_id][date_iso] = flag
                                    self._flag_colors_cache[user_id][date_iso] = self.FLAG_COLORS.get(flag, "transparent")
                                    
                                    # Get comment and hours from HR calendar
                                    hr_comment = self._comments_cache.get(hr_id, {}).get(date_iso, "")
                                    hr_hours = self._hours_cache.get(hr_id, {}).get(date_iso, 0.0)
                                    
                                    # Update caches
                                    if hr_comment and not self._comments_cache[user_id].get(date_iso):
                                        self._comments_cache[user_id][date_iso] = hr_comment
                                    if hr_hours > 0 and not self._hours_cache[user_id].get(date_iso):
                                        self._hours_cache[user_id][date_iso] = hr_hours
                                    
                                    # Create history entry for inherited flag
                                    entry = {
                                        "timestamp": timestamp,
                                        "action": "inherited from project HR",
                                        "comment": hr_comment,
                                        "flag": flag,
                                        "hours": hr_hours,
                                        "user": self.current_user_name,
                                        "user_role": self.current_user_role
                                    }
                                    
                                    if date_iso not in self.history[user_id]:
                                        self.history[user_id][date_iso] = []
                                    self.history[user_id][date_iso].append(entry)
                    
                    # Break after first HR user (we only need one source)
                    break
            
            return {
                "success": True,
                "message": f"Successfully imported calendar for new user: {user_name} ({len(days)} days)"
            }
        
        else:
            # EXISTING EMPLOYEE SCENARIO
            # Only import non-HR flags, merge with existing data
            days = import_data.get("days", [])
            imported_count = 0
            skipped_hr_flags = 0
            
            # Initialize if needed
            if user_id not in self.history:
                self.history[user_id] = {}
            if user_id not in self._comments_cache:
                self._comments_cache[user_id] = {}
            if user_id not in self._flags_cache:
                self._flags_cache[user_id] = {}
            if user_id not in self._hours_cache:
                self._hours_cache[user_id] = {}
            if user_id not in self._flag_colors_cache:
                self._flag_colors_cache[user_id] = {}
            
            for day in days:
                date_iso = day.get("date", "")
                flag = day.get("flag", "")
                comment = day.get("comment", "")
                hours = day.get("hours", 0.0)
                
                if not date_iso:
                    continue
                
                # Skip HR-only flags for existing users
                if flag in self.HR_ONLY_FLAGS:
                    skipped_hr_flags += 1
                    continue
                
                # Create history entry
                entry = {
                    "timestamp": timestamp,
                    "action": "imported (merged)",
                    "comment": comment,
                    "flag": flag,
                    "hours": hours,
                    "user": self.current_user_name,
                    "user_role": self.current_user_role
                }
                
                if date_iso not in self.history[user_id]:
                    self.history[user_id][date_iso] = []
                self.history[user_id][date_iso].append(entry)
                
                # Update caches (overwrite existing)
                self._comments_cache[user_id][date_iso] = comment
                self._flags_cache[user_id][date_iso] = flag
                self._hours_cache[user_id][date_iso] = hours
                if flag:
                    self._flag_colors_cache[user_id][date_iso] = self.FLAG_COLORS.get(flag, "transparent")
                elif date_iso in self._flag_colors_cache[user_id]:
                    del self._flag_colors_cache[user_id][date_iso]
                
                imported_count += 1
            
            # Update validation status to PENDING_MANAGER
            old_status = self.calendar_status.get(user_id, self.STATUS_DRAFT)
            if old_status != self.STATUS_PENDING_MANAGER:
                self.calendar_status[user_id] = self.STATUS_PENDING_MANAGER
                self._log_status_change(
                    user_id, 
                    old_status, 
                    self.STATUS_PENDING_MANAGER, 
                    f"Calendar imported: {imported_count} days updated"
                )
            
            msg = f"Successfully imported calendar for {user_name} ({imported_count} days)"
            if skipped_hr_flags > 0:
                msg += f". Skipped {skipped_hr_flags} HR-only flags."
            
            return {
                "success": True,
                "message": msg
            }

    @rx.var
    def get_month_name(self) -> str:

        month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
        ]
        """Get month name from month number."""
        if 1 <= self.selected_month <= 12:
            return month_names[self.selected_month - 1]
        return "Unknown"
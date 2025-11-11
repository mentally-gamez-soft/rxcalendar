# Multi-Tenant Project-Based Calendar Implementation

## Overview
Successfully transformed the single-tenant calendar into a **multi-tenant, project-based system** with:
- ✅ 3 Projects (Atlas, Phoenix, Horizon)
- ✅ 17 Users distributed across projects
- ✅ Per-user calendars with project association
- ✅ Role-based calendar visibility (Employee/Manager/HR)
- ✅ Read/Write permission management
- ✅ Project-grouped UI with visual indicators

---

## Architecture Changes

### 1. Data Model

#### **Before:**
```python
# Single shared calendar for all users
history: dict[str, list[dict]] = {}  # {date: [entries]}
```

#### **After:**
```python
# Per-user calendars linked to projects
history: dict[str, dict[str, list[dict]]] = {}  # {user_id: {date: [entries]}}

# Project domain
class Project(TypedDict):
    id: str
    name: str
    description: str

# Updated User model
class User(TypedDict):
    id: str
    name: str
    role: str  # "employee", "manager", "hr"
    project_id: str  # NEW: Link to project
```

### 2. Project Definitions

**Project Atlas** - Global Infrastructure Project
- 4 Employees: Alice Johnson, Bob Smith, Charlie Brown, Diana Prince
- 1 Manager: Kevin Anderson
- 1 HR: Michael Scott

**Project Phoenix** - Digital Transformation Initiative
- 4 Employees: Ethan Hunt, Fiona Green, George Wilson, Hannah White
- 1 Manager: Laura Martinez
- 2 HR: Nancy Drew, Oscar Wilde

**Project Horizon** - Future Innovation Lab
- 2 Employees: Ian Malcolm, Julia Roberts
- 1 Manager: Marcus Lee
- 2 HR: Patricia Hill, Quincy Adams

---

## Permission System

### Calendar Visibility Rules

| Role | Can View | Can Edit |
|------|----------|----------|
| **Employee** | Own calendar only | Own calendar only |
| **Manager** | All project team calendars | Own calendar only |
| **HR** | All calendars (cross-project) | All calendars (cross-project) |

### Access Control Flow

1. **Login User**: Current user (who is logged in)
2. **Viewed User**: Whose calendar is being displayed
3. **Permission Check**: 
   - Reading: Uses `viewed_user_id` to display data
   - Writing: Requires `can_edit_viewed_calendar` check

### Key State Variables

```python
current_user_id: str  # Who is logged in
viewed_user_id: str   # Whose calendar is displayed
```

---

## UI Components

### Header Layout (Option B Style)

```
┌───────────────────────────────────────────────────────┐
│ 2026 Calendar              Current User: Alice (🔵)  │
│ Click weekdays...          [Switch User]      [Export]│
├───────────────────────────────────────────────────────┤
│ 🏢 Project: Atlas          [Viewing: Bob Smith] 🔴RO  │
├───────────────────────────────────────────────────────┤
│ View Calendar: (Manager/HR only)                      │
│   Atlas                                               │
│   [Alice] [Bob] [Charlie] [Diana] [Kevin] [Michael]  │
└───────────────────────────────────────────────────────┘
```

### User Selector Dialog

Users are now **grouped by project**:
```
┌─────────────────────────────┐
│ Switch User                 │
├─────────────────────────────┤
│ 🏢 Project: Atlas           │
│   • Alice Johnson      ✓    │
│   • Bob Smith               │
│   • Charlie Brown           │
│   • Diana Prince            │
│   • Kevin Anderson (Mgr)    │
│   • Michael Scott (HR)      │
├─────────────────────────────┤
│ 🏢 Project: Phoenix         │
│   • Ethan Hunt              │
│   • ...                     │
└─────────────────────────────┘
```

### Calendar View Selector (Manager/HR)

Compact button interface to switch between team calendars:
```
View Calendar:
Atlas
  [Alice] [Bob] [Charlie] [Diana] [Kevin] [Michael]

Phoenix
  [Ethan] [Fiona] [George] [Hannah] [Laura] [Nancy] [Oscar]
```

---

## Implementation Details

### 1. Data Access Pattern

**Reading Data (Display):**
```python
# Always use viewed_user_id
user_id = self.viewed_user_id
flag = self._flags_cache[user_id].get(date_iso, "")
```

**Writing Data (Modifications):**
```python
# Check permission first
if not self.can_edit_viewed_calendar:
    return rx.toast.error("Access Denied: Read-only")

# Write to viewed user's calendar
user_id = self.viewed_user_id
self.history[user_id][date_iso].append(entry)
```

### 2. Key Computed Variables

```python
@rx.var
def visible_users(self) -> list[dict]:
    """Users whose calendars current user can see."""
    if role == "hr":
        return all_users  # Cross-project access
    elif role == "manager":
        return users_in_same_project
    else:  # employee
        return [current_user]  # Self only

@rx.var
def can_edit_viewed_calendar(self) -> bool:
    """Can current user edit the viewed calendar?"""
    if viewed == current:
        return True  # Own calendar
    if current_role == "hr":
        return True  # HR can edit any
    return False  # Manager read-only for others
```

### 3. Method Updates

All data access methods updated to support user-specific calendars:

- ✅ `save_comment()` - Writes to viewed user's calendar
- ✅ `handle_day_click()` - Checks edit permissions
- ✅ `get_flag_for_date()` - Reads from viewed user's calendar
- ✅ `get_hours_for_date()` - Reads from viewed user's calendar
- ✅ `get_comment_for_date()` - Reads from viewed user's calendar
- ✅ `export_to_json()` - Exports current user's calendar with project info

### 4. New Methods

```python
def view_user_calendar(self, user_id: str):
    """Switch to viewing another user's calendar (Manager/HR)."""
    # Permission check + update viewed_user_id
    
def switch_user(self, user_id: str):
    """Switch logged-in user (simulates login)."""
    # Updates current_user_id and viewed_user_id
```

---

## Usage Scenarios

### Scenario 1: Employee (Alice - Atlas)
1. Logs in as Alice Johnson
2. Sees only her own calendar
3. Project badge shows "Project: Atlas"
4. Can edit her calendar freely
5. Cannot see Bob's or anyone else's calendar

### Scenario 2: Manager (Kevin - Atlas)
1. Logs in as Kevin Anderson (Manager)
2. Sees calendar view selector with 6 Atlas team members
3. Can view Alice's, Bob's, Charlie's, Diana's, Michael's calendars
4. **Read-only** access to team calendars
5. Can only edit his own calendar
6. Cannot see Phoenix or Horizon calendars

### Scenario 3: HR (Michael - Atlas)
1. Logs in as Michael Scott (HR)
2. Sees **all 17 users** in calendar view selector
3. Can view ANY user's calendar (cross-project)
4. Can **edit ANY calendar** (read+write all)
5. Can set HR-only flags (national day off, etc.) on any calendar

### Scenario 4: Manager Viewing Team
1. Kevin (Manager) clicks [Bob] in calendar view selector
2. Header shows: "🏢 Project: Atlas | Viewing: Bob Smith 🔴 Read-Only"
3. Bob's calendar displays with all his flags/comments
4. Kevin clicks on a date → Error: "Access Denied: Read-only"
5. Kevin can switch back to his own calendar to edit

### Scenario 5: HR Cross-Project Access
1. Michael (HR - Atlas project) clicks [Ethan] (Phoenix project)
2. Header shows: "🏢 Project: Phoenix | Viewing: Ethan Hunt"
3. Can view AND edit Ethan's calendar
4. Can set HR-only flags on Ethan's dates
5. Changes are saved to Ethan's personal calendar

---

## Data Isolation

### Complete Separation
- ✅ Each user has their own `history` dictionary
- ✅ Each user has their own cache dictionaries
- ✅ Alice's "Jan 15" entry is completely independent from Bob's "Jan 15" entry
- ✅ Managers cannot accidentally modify team calendars
- ✅ Employees cannot see other employees' calendars

### Export Behavior
```json
{
  "year": 2026,
  "user": "Alice Johnson",
  "project": "Atlas",
  "entries": [
    // Only Alice's calendar entries
  ]
}
```

---

## Testing Checklist

### ✅ Completed Tests

1. **User Switching**
   - [x] Switch between users in same project
   - [x] Switch between users in different projects
   - [x] User selector groups by project correctly

2. **Data Isolation**
   - [x] Alice's calendar independent from Bob's
   - [x] Edits to Alice's calendar don't affect Bob's
   - [x] Each user starts with empty calendar

3. **RBAC (Role-Based Access Control)**
   - [x] Employees see only own calendar
   - [x] Managers see team calendars
   - [x] HR sees all calendars
   - [x] Flag permissions still work (HR-only, Manager-only)

4. **Manager Read Access**
   - [x] Manager can view team calendars
   - [x] Manager blocked from editing others' calendars
   - [x] "Read-Only" badge displays correctly

5. **HR Cross-Project Access**
   - [x] HR can view any user's calendar
   - [x] HR can edit any user's calendar
   - [x] HR can set HR-only flags on any calendar

6. **UI/UX**
   - [x] Project badge displays correctly
   - [x] "Viewing: [User]" badge shows for non-self calendars
   - [x] Calendar view selector appears for Manager/HR only
   - [x] User selector groups by project

7. **Range Selection**
   - [x] Range selection works with new per-user structure
   - [x] HR-only protection still enforced in ranges

---

## Technical Constraints

### Maintained from Original System
- ✅ Append-only history (no deletion)
- ✅ HR-only flags protection
- ✅ Range selection support
- ✅ History tracking with timestamps
- ✅ Flag-based permissions

### New Constraints
- ✅ One employee = One project (1:1)
- ✅ One calendar = One project (via user)
- ✅ Manager visibility limited to project
- ✅ HR has global visibility

---

## Performance Considerations

### Cache Strategy
```python
# Per-user caches for fast lookups
_comments_cache: dict[str, dict[str, str]] = {}
# Structure: {user_id: {date: comment}}
```

### Initialization
- Lazy initialization: User calendars created on first write
- No upfront memory allocation for all 17 users
- Only active users consume memory

---

## Future Enhancements

### Potential Improvements
1. **Project-level aggregated views** (team calendar overview)
2. **Multi-project assignments** (users in multiple projects)
3. **Project-specific holidays** (HR manages per-project)
4. **Delegation** (employees delegate calendar to managers)
5. **Audit logs** (who viewed which calendar when)
6. **Calendar sharing** (share read access temporarily)
7. **Bulk operations** (HR sets holidays for entire project)

---

## Migration Notes

### Breaking Changes
- ⚠️ **Data structure changed**: Old shared calendar incompatible
- ⚠️ **Fresh start**: All existing calendar data reset
- ⚠️ **User IDs**: emp001-emp010, mgr001-mgr003, hr001-hr005

### Backward Compatibility
- ❌ Old saved calendars cannot be imported
- ✅ All existing features preserved (flags, hours, comments, range selection)
- ✅ RBAC system enhanced (not replaced)

---

## Deployment Checklist

### Pre-Deployment
- [x] Update state.py with project model
- [x] Update all data access methods
- [x] Update UI components
- [x] Test all user roles
- [x] Test cross-project access
- [x] Verify data isolation

### Post-Deployment
- [ ] Monitor for permission errors
- [ ] Verify no cross-user data leakage
- [ ] Test with real user scenarios
- [ ] Gather feedback on UX

---

## Support & Troubleshooting

### Common Issues

**Issue:** "Access Denied: You can only view [User]'s calendar"
- **Cause:** Manager trying to edit team member's calendar
- **Solution:** Switch to own calendar to make edits

**Issue:** Can't see other project calendars
- **Cause:** Manager role is project-scoped
- **Solution:** Switch to HR role for cross-project access

**Issue:** Calendar appears empty after switching users
- **Cause:** New user hasn't added any entries yet
- **Solution:** This is correct behavior (data isolation)

---

## Technical Stack

- **Framework:** Reflex 0.8.18
- **Language:** Python 3.13.5
- **Architecture:** Client-server (WebSocket state sync)
- **Data Model:** In-memory dictionaries (per-user)
- **Deployment:** Port 3023 (frontend), 8023 (backend)

---

## Success Criteria ✅

All requirements met:
- ✅ Introduced project domain (Atlas, Phoenix, Horizon)
- ✅ Assigned employees to projects (1:1 constraint)
- ✅ Each employee has own calendar
- ✅ Each calendar linked to project
- ✅ Project name visible in UI (Option B style)
- ✅ Data isolation between users
- ✅ Manager read access to team
- ✅ HR cross-project read+write access
- ✅ User selector grouped by project

---

## Conclusion

The calendar application has been successfully transformed from a **single-tenant shared calendar** to a **multi-tenant, project-based system** with comprehensive role-based access controls. Each user now has their own calendar linked to their project, with appropriate visibility and edit permissions based on their role.

**App running at:** http://localhost:3023/

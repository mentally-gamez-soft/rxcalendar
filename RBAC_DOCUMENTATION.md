# Role-Based Access Control (RBAC) Documentation

## Overview
The calendar application now implements a comprehensive role-based access control system with three distinct user roles, each with specific permissions for setting day flags.

## User Roles

### 1. Standard Employee
**Permissions:**
- Can set the following flag types:
  - `extra day off`
  - `on vacation`
  - `(blank)` - no flag

**Restrictions:**
- Cannot set HR-only flags (national/regional holidays, Akkodis offered days)
- Cannot set manager/HR flags (offered vacation, vacation client closed)

### 2. Manager
**Permissions:**
- All employee permissions, plus:
  - `offered vacation client closed`
  - `on vacation client closed`
  - `extra day off`
  - `on vacation`
  - `(blank)` - no flag

**Restrictions:**
- Cannot set HR-only flags (national/regional holidays, Akkodis offered days)

### 3. HR Services
**Permissions:**
- Full access to all flag types:
  - `national day off`
  - `Akkodis offered day off`
  - `regional day off`
  - `offered vacation client closed`
  - `on vacation client closed`
  - `extra day off`
  - `on vacation`
  - `(blank)` - no flag

**Restrictions:**
- None - HR has complete access

## Dummy Users

### Employees (10 users)
1. Alice Johnson (emp001)
2. Bob Smith (emp002)
3. Charlie Brown (emp003)
4. Diana Prince (emp004)
5. Ethan Hunt (emp005)
6. Fiona Green (emp006)
7. George Wilson (emp007)
8. Hannah White (emp008)
9. Ian Malcolm (emp009)
10. Julia Roberts (emp010)

### Managers (2 users)
1. Kevin Anderson (mgr001)
2. Laura Martinez (mgr002)

### HR Services (5 users)
1. Michael Scott (hr001)
2. Nancy Drew (hr002)
3. Oscar Wilde (hr003)
4. Patricia Hill (hr004)
5. Quincy Adams (hr005)

## Implementation Details

### Data Structure

#### User Object
```python
{
    "id": "emp001",
    "name": "Alice Johnson",
    "role": "employee"  # "employee", "manager", or "hr"
}
```

#### History Entry (Enhanced)
Each history entry now includes user information:
```python
{
    "timestamp": "2026-01-15 14:30:00",
    "action": "comment added, flag changed",
    "comment": "Taking vacation",
    "flag": "on vacation",
    "hours": 0.0,
    "user": "Alice Johnson",
    "user_role": "employee"
}
```

### Permission Logic

#### Flag Permission Matrix

| Flag Type | Employee | Manager | HR |
|-----------|----------|---------|-----|
| (blank) | ✅ | ✅ | ✅ |
| extra day off | ✅ | ✅ | ✅ |
| on vacation | ✅ | ✅ | ✅ |
| offered vacation client closed | ❌ | ✅ | ✅ |
| on vacation client closed | ❌ | ✅ | ✅ |
| national day off | ❌ | ❌ | ✅ |
| Akkodis offered day off | ❌ | ❌ | ✅ |
| regional day off | ❌ | ❌ | ✅ |

### Code Implementation

#### State Management (state.py)

```python
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
```

#### Permission Check
```python
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
```

### UI Components

#### User Selector Dialog
- Displays all 17 dummy users organized by role
- Shows current user with checkmark
- Color-coded badges:
  - Gray: Employees
  - Blue: Managers
  - Purple: HR Services

#### Dynamic Flag Selector
- Automatically filters available flags based on current user's role
- Uses `rx.foreach` to dynamically generate options
- Only shows flags the user has permission to set

#### Header Enhancement
- Displays current user name with role badge
- "Switch User" button to open user selector
- Color-coded by role (gray/blue/purple)

## User Experience

### Switching Users
1. Click "Switch User" button in header
2. Select a user from the organized list
3. System confirms switch with toast notification
4. Flag selector automatically updates with available options

### Attempting Unauthorized Action
1. User selects a flag they don't have permission for
2. On save, system shows error toast:
   ```
   "Access Denied: Employees cannot set 'national day off' flag"
   ```
3. Dialog remains open for user to correct their selection

### Audit Trail
- Every history entry includes:
  - User who made the change
  - User's role at time of change
  - All other standard fields (timestamp, action, comment, flag, hours)

## Security Features

1. **Client-side Validation**: Flag selector only shows permitted flags
2. **Server-side Validation**: `save_comment()` validates permissions before saving
3. **Audit Trail**: Complete record of who made each change
4. **Clear Error Messages**: Users understand why they can't perform an action

## Testing Scenarios

### Test Case 1: Employee Restrictions
1. Switch to employee (e.g., Alice Johnson)
2. Try to set "national day off" flag
3. Expected: Flag not available in dropdown

### Test Case 2: Manager Permissions
1. Switch to manager (e.g., Kevin Anderson)
2. Set "offered vacation client closed" flag
3. Expected: Save succeeds

### Test Case 3: HR Full Access
1. Switch to HR (e.g., Michael Scott)
2. Set "national day off" flag
3. Expected: Save succeeds
4. View history to see HR user recorded

### Test Case 4: Audit Trail
1. Make changes as different users
2. View history for a date
3. Expected: Each entry shows user name and role badge

## Future Enhancements

1. **Persistent Authentication**: Replace dummy users with real authentication
2. **Database Integration**: Store user credentials and roles
3. **Advanced Permissions**: Fine-grained permissions per user
4. **User Management UI**: Admin interface to manage users and roles
5. **Session Management**: Proper login/logout functionality
6. **Role Hierarchies**: More complex role structures
7. **Approval Workflows**: Require manager approval for certain flags

## API Reference

### State Properties

- `current_user_id: str` - Currently selected user ID
- `current_user: dict` - Current user object (computed)
- `current_user_role: str` - Current user's role (computed)
- `current_user_name: str` - Current user's display name (computed)
- `allowed_flags: list[tuple]` - Flags available to current user (computed)

### State Methods

- `switch_user(user_id: str)` - Change current user
- `toggle_user_selector()` - Open/close user selector dialog
- `can_modify_flag(flag: str) -> bool` - Check flag permission

### Components

- `user_selector_dialog()` - User selection interface
- `flag_selector()` - Dynamic flag dropdown based on role
- Header enhanced with user display and switch button

## Color Scheme

**User Role Badges:**
- Employee: Gray (`color_scheme="gray"`)
- Manager: Blue (`color_scheme="blue"`)
- HR Services: Purple (`color_scheme="purple"`)

**Flag Colors (unchanged):**
- offered vacation client closed: Red (#e53e3e)
- national day off: Orange (#dd6b20)
- Akkodis offered day off: Blue (#3182ce)
- on vacation: Purple (#805ad5)
- on vacation client closed: Green (#2f855a)
- regional day off: Pink (#d53f8c)
- extra day off: Gray (#718096)

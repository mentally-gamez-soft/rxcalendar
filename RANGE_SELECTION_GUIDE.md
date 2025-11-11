# Range Selection & HR-Only Protection Features

## Overview
The calendar application now supports selecting date ranges and includes HR-only protection for sensitive flag types.

---

## Feature 1: Range Selection

### How It Works

1. **First Click** - Select Start Date:
   - Click on any weekday to set the range start
   - A "START" badge appears on the selected day
   - Blue border highlights the start date
   - Toast notification: "Range Start: [date] - Click another day to complete range"

2. **Second Click** - Select End Date:
   - Click another weekday to complete the range
   - End date must be on or after start date
   - System calculates all weekdays in range (Saturdays/Sundays excluded)
   - Dialog opens showing: "Range: [start] to [end]"
   - Toast shows number of weekdays: "Range Selected: X weekday(s)"

3. **Single Day Selection**:
   - Click the same day twice to select only that day
   - Acts as a single date entry

### Visual Feedback

- **Range Start**: Blue "START" badge + thick blue border
- **Hover Effect**: When selecting end date, hovering over days shows potential range
- **Calendar Interaction**: Only weekdays (Mon-Fri) are selectable

### Range Application

- **Comment**: Applied to ALL weekdays in range
- **Flag**: Same flag set for ALL weekdays in range  
- **Hours**: Same hours value for ALL weekdays in range
- **Weekends**: Automatically excluded from range

### Example Workflow

```
User wants to mark vacation from Jan 13-17, 2026:

1. Click "Wed Jan 15, 2026" → Range start set
2. Click "Fri Jan 17, 2026" → Range complete
3. Dialog shows: "Range: 2026-01-13 to 2026-01-17"
4. Enter: Comment: "Winter Vacation"
5. Select Flag: "on vacation"
6. Click Save
7. Result: 5 weekdays updated (Mon-Fri)
```

### Canceling Range Selection

- Click "Cancel" in dialog to reset range
- Close dialog to start over
- Range resets after successful save

---

## Feature 2: HR-Only Protection

### Protected Flag Types

Only HR Services can modify days with these flags:
- ❌ **national day off**
- ❌ **Akkodis offered day off**
- ❌ **regional day off**

### Protection Rules

#### Single Date Selection
- If Employee/Manager clicks a day with HR-only flag:
  - ❌ **Access Denied** - Immediate error message
  - Dialog does not open
  - Error toast: "Only HR can modify days with '[flag name]' flag"

#### Range Selection
- If range includes HR-protected dates:
  - ✅ **Partial Save** - System skips protected dates
  - ✅ Only modifies allowed dates in range
  - ⚠️ Warning toast shows:
    - Number of dates saved
    - Number of dates skipped
    - Example: "Saved 3 date(s). Skipped 2 HR-protected date(s)"

### Permission Matrix

| Flag Type | Employee | Manager | HR | Protection |
|-----------|----------|---------|-----|------------|
| (blank) | ✅ | ✅ | ✅ | None |
| extra day off | ✅ | ✅ | ✅ | None |
| on vacation | ✅ | ✅ | ✅ | None |
| offered vacation client closed | ❌ | ✅ | ✅ | Role-based |
| on vacation client closed | ❌ | ✅ | ✅ | Role-based |
| **national day off** | ❌ | ❌ | ✅ | **HR-Only** |
| **Akkodis offered day off** | ❌ | ❌ | ✅ | **HR-Only** |
| **regional day off** | ❌ | ❌ | ✅ | **HR-Only** |

### Example Scenarios

#### Scenario 1: Employee Tries to Edit National Holiday

```
Current User: Alice Johnson (Employee)
Date: Dec 25, 2026
Current Flag: "national day off" (set by HR)

Action: Alice clicks Dec 25
Result: ❌ Error toast immediately
Message: "Access Denied: Only HR can modify days with 'national day off' flag"
Dialog: Does not open
```

#### Scenario 2: Manager Edits Vacation Range with HR-Protected Days

```
Current User: Kevin Anderson (Manager)
Range: Dec 20-31, 2026
Existing Data:
  - Dec 25: "national day off" (HR-protected)
  - Dec 26: "regional day off" (HR-protected)
  - Other days: Available

Action: Kevin selects range Dec 20-31 and sets flag "on vacation"
Result: ✅ Partial save
  - Dec 20-24: ✅ Saved with "on vacation"
  - Dec 25: ⚠️ Skipped (HR-protected)
  - Dec 26: ⚠️ Skipped (HR-protected)
  - Dec 27-31 (weekdays): ✅ Saved with "on vacation"
  
Toast: "Saved 8 date(s). Skipped 2 HR-protected date(s)"
```

#### Scenario 3: HR Modifies Everything

```
Current User: Michael Scott (HR)
Range: Any range
Any existing flags: No restrictions

Action: HR can modify any date with any flag
Result: ✅ All dates in range are updated
No dates are skipped
```

---

## Technical Implementation

### State Variables

```python
# Range selection
range_start_date: str = ""       # ISO format: "YYYY-MM-DD"
range_end_date: str = ""         # ISO format: "YYYY-MM-DD"
is_selecting_range: bool = False # Flag for UI feedback
hovered_date: str = ""           # For hover effects
```

### Key Methods

#### `handle_day_click(day_str: str)`
- Manages range selection state machine
- Validates weekday and date order
- Checks HR-only protection for single dates

#### `save_comment()`
- Applies changes to all weekdays in range
- Filters out HR-protected dates for non-HR users
- Creates history entries for each modified date
- Shows appropriate success/warning messages

#### `can_edit_date(date_iso: str) -> bool`
- Checks if current user can modify a specific date
- Returns False if date has HR-only flag and user is not HR
- Used for both single date and range validation

#### `get_weekdays_in_range(start_date: str, end_date: str) -> list[str]`
- Calculates all weekdays between two dates
- Excludes weekends automatically
- Returns list of ISO date strings

---

## UI Indicators

### Calendar Cell States

1. **Normal Weekday**: Light background, clickable
2. **Range Start**: Blue "START" badge, thick blue border
3. **Weekend**: Gray background, not clickable, "not-allowed" cursor
4. **HR-Protected**: Normal appearance, but blocked on click (if not HR)

### Toast Notifications

- **Range Start**: Blue info toast
- **Range Complete**: Blue info toast with weekday count
- **Access Denied**: Red error toast (5 second duration)
- **Partial Save**: Yellow warning toast with details (5 second duration)
- **Full Save**: Green success toast

### Dialog Behavior

- **Title**: Shows single date or "Range: [start] to [end]"
- **Description**: Indicates if applying to range
- **Single input**: Same values applied to all dates in range

---

## User Experience Guidelines

### Best Practices

1. **Visual Feedback**: Always look for the "START" badge when selecting ranges
2. **Date Order**: Always select end date after or same as start date
3. **Weekday Focus**: Remember only Mon-Fri are affected by ranges
4. **HR Protection**: Check toast messages for skipped dates
5. **Cancel Anytime**: Use Cancel button to reset incomplete selections

### Common Workflows

#### Mark Week-Long Vacation
1. Click Monday (start)
2. Click Friday (end)
3. Set flag "on vacation"
4. Save → 5 weekdays updated

#### Mark Single Sick Day
1. Click desired date
2. Click same date again (or just once if dialog opens)
3. Set flag "sick leave"
4. Save → 1 day updated

#### HR Sets Company Holidays
1. Switch to HR user
2. Click each national holiday individually
3. Set flag "national day off"
4. Save each date
5. Now protected from employee/manager edits

---

## Troubleshooting

### "End date cannot be before start date"
**Solution**: Click a later date or the same date for single selection

### "All selected dates are HR-protected"
**Solution**: Switch to HR user or select different dates

### "Saved X dates. Skipped Y dates"
**Explanation**: Some dates in your range were HR-protected. Check which dates have HR-only flags.

### Range selection stuck
**Solution**: Click Cancel in dialog or refresh page to reset state

---

## Technical Notes

### Date Format
- Internal storage: ISO 8601 format (`YYYY-MM-DD`)
- Display format: Human-readable (`January 15, 2026`)
- Range display: `[start] to [end]`

### History Tracking
- Each date in range gets its own history entry
- All entries share same timestamp
- User and action recorded for each entry

### Performance
- Range calculation: O(n) where n = days in range
- Protection check: O(1) per date (cache lookup)
- Max recommended range: 1 year (366 dates)

---

## Future Enhancements

Potential improvements:
1. Visual range preview during hover
2. Weekday count display during selection
3. Bulk undo for range operations
4. Range templates (e.g., "full week", "full month")
5. Multi-range selection (Ctrl+Click)
6. Range exclusions (skip specific dates within range)

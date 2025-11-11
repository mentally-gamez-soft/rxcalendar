# History Tracking Feature

## Overview
The calendar application now includes comprehensive history tracking for all changes made to dates. This implements a complete audit trail system that records every modification.

## Implementation Details

### Data Structure
The history system uses an append-only data model:

```python
history: dict[str, list[dict]] = {}
```

Each date maps to a list of history entries, where each entry contains:
- `timestamp`: ISO format datetime string (YYYY-MM-DD HH:MM:SS)
- `action`: Description of what changed (e.g., "comment added", "flag changed, hours changed")
- `comment`: The comment text (may be empty)
- `flag`: The flag value (may be empty for blank)
- `hours`: Float value between 0 and 12

### Key Features

1. **Append-Only Model**: New saves never overwrite previous entries. Each save creates a new history entry.

2. **Computed Current Values**: The application maintains cached dictionaries for current values:
   - `_comments_cache`: Current comment per date
   - `_flags_cache`: Current flag per date
   - `_hours_cache`: Current hours per date
   - `_flag_colors_cache`: Current flag color per date

3. **Action Tracking**: Each save automatically detects what changed by comparing new values against cached values and generates an appropriate action description:
   - "comment added" (when comment goes from empty to filled)
   - "comment modified" (when comment changes)
   - "flag changed" (when flag selection changes)
   - "hours changed" (when hours value changes and no flag is set)

4. **UI Components**:
   - **Main Dialog**: Shows current values (editable)
   - **View History Button**: Opens history dialog (disabled if no history exists)
   - **History Dialog**: Displays all changes in chronological order with:
     - Timestamp badges
     - Action badges
     - All values from each entry (comment, flag, hours)

5. **Export Format**: The JSON export now includes both current values and full history:
```json
{
  "year": 2026,
  "entries": [
    {
      "date": "2026-01-15",
      "day_name": "Thursday",
      "formatted_date": "January 15, 2026",
      "current": {
        "comment": "Latest comment",
        "flag": "vacation",
        "hours": 0.0
      },
      "history": [
        {
          "timestamp": "2026-01-10 14:30:00",
          "action": "comment added",
          "comment": "First comment",
          "flag": "",
          "hours": 8.0
        },
        {
          "timestamp": "2026-01-11 09:15:00",
          "action": "flag changed, hours changed",
          "comment": "First comment",
          "flag": "vacation",
          "hours": 0.0
        }
      ]
    }
  ]
}
```

## User Experience

### Adding/Modifying Entries
1. Click on a weekday to open the dialog
2. Current values are pre-filled (from latest history entry)
3. Make changes and click Save
4. A new history entry is created with timestamp and action

### Viewing History
1. Click on a date that has existing data
2. Click "View History" button in the dialog
3. See all changes in chronological order (newest first)
4. Each entry shows timestamp, action taken, and all values at that point

### Data Integrity
- **No Overwrites**: Previous entries remain intact forever
- **Complete Audit Trail**: Every change is tracked with timestamp and action
- **Automatic Action Detection**: System automatically determines what changed
- **Cached Performance**: Current values are cached for fast access without scanning history

## Technical Benefits

1. **Audit Trail**: Complete history of all changes for compliance/tracking
2. **Data Recovery**: Can see previous values if needed
3. **Change Analysis**: Can analyze what changes were made and when
4. **No Data Loss**: Accidental changes don't lose previous information

## Example Usage Flow

```
Day: 2026-01-15

History Entry 1 (2026-01-10 14:30:00):
- Action: "comment added"
- Comment: "Meeting with client"
- Flag: ""
- Hours: 8.0

History Entry 2 (2026-01-11 09:15:00):
- Action: "flag changed, hours changed"
- Comment: "Meeting with client"
- Flag: "vacation"
- Hours: 0.0

History Entry 3 (2026-01-12 16:45:00):
- Action: "comment modified"
- Comment: "On vacation - client meeting rescheduled"
- Flag: "vacation"
- Hours: 0.0

Current Values (displayed in dialog):
- Comment: "On vacation - client meeting rescheduled"
- Flag: "vacation"
- Hours: 0.0
```

## Code Organization

### state.py
- `history`: Main data structure
- `_*_cache`: Cached current values
- `history_entries_for_selected`: Computed property for history dialog
- `save_comment()`: Appends new history entry
- `open_history_dialog()` / `close_history_dialog()`: Dialog management

### components.py
- `comment_dialog()`: Main entry dialog with "View History" button
- `history_dialog()`: Displays full history timeline
- `history_entry_card()`: Renders individual history entries

### Export
- `export_to_json()`: Includes both current values and full history array per date

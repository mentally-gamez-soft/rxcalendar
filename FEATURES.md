# 2026 Calendar Application - Feature Summary

## Overview
A Reflex-based web application for managing a 2026 calendar with comments, flags, and hours tracking for weekdays.

## Features Implemented

### 1. Calendar Display
- **12-month grid layout** showing all months of 2026
- **Weekday highlighting** (Monday-Friday are interactive)
- **Weekend distinction** (Saturday-Sunday are disabled)
- **Color-coded days** based on flag status

### 2. Day Flags
Users can set one of the following flags for each weekday:
- **(blank)** - Regular working day
- **National day off** - Red (#e53e3e)
- **Akkodis offered day off** - Orange (#dd6b20)
- **On vacation** - Blue (#3182ce)
- **On vacation client closed** - Purple (#805ad5)
- **Offered vacation client closed** - Green (#2f855a)
- **Regional day off** - Pink (#d53f8c)
- **Extra day off** - Gray (#718096)

### 3. Hours Tracking
- **Hours input** available when no flag is set (blank)
- **Range**: 0 to 12 hours
- **Step**: 0.5 hours
- **Auto-reset**: Hours automatically set to 0 when a flag is chosen
- **Display**: Hours shown on calendar cell when > 0

### 4. Comments
- **Text comments** can be added to any weekday
- **Persistent storage** across sessions (in state)
- **Dialog interface** for easy editing

### 5. Visual Legend
- **Color legend** displayed below the calendar grid
- Shows all flag types with their corresponding colors
- Helps users quickly understand day status

### 6. Export Functionality
- **JSON export** button in header
- Exports all calendar data including:
  - Date (YYYY-MM-DD)
  - Day name (e.g., "Monday")
  - Formatted date (e.g., "January 15, 2026")
  - Comment (if present)
  - Flag (if set)
  - Hours (if > 0)

## Usage

### Adding Data to a Day
1. Click on any weekday (Monday-Friday) in the calendar
2. A dialog appears with fields for:
   - **Comment**: Free text input
   - **Flag**: Dropdown selector
   - **Hours**: Number input (0-12, step 0.5)
3. Click "Save" to persist changes

### Flag and Hours Rules
- **When a flag is set**: Hours are automatically forced to 0
- **When flag is blank**: Hours can be set between 0 and 12
- **Color indication**: Each flag has a unique color shown on the calendar cell

### Exporting Data
- Click the "Export Comments as JSON" button in the top-right
- Downloads `calendar_2026_data.json` with all entries

## File Structure

```
rxcalendar/
├── __init__.py
├── state.py              # State management (comments, flags, hours)
├── components.py         # UI components (dialog, header, grid, legend)
├── custom_calendar.py    # Custom calendar renderer with color support
└── rxcalendar.py        # Main app entry point
```

## Technical Details

### State Management (`state.py`)
- **comments**: `dict[str, str]` - Date -> comment mapping
- **flags**: `dict[str, str]` - Date -> flag mapping
- **hours**: `dict[str, float]` - Date -> hours mapping
- **flag_colors_by_date**: `dict[str, str]` - Computed color per date

### Component Architecture
- **Separation of concerns**: State logic separate from UI
- **Reusable components**: Month calendar, dialog, legend
- **Reactive updates**: UI updates automatically when state changes

### Flag Color Mapping
```python
FLAG_COLORS = {
    "": "var(--white)",
    "national day off": "#e53e3e",
    "Akkodis offered day off": "#dd6b20",
    "on vacation": "#3182ce",
    "on vacation client closed": "#805ad5",
    "offered vacation client closed": "#2f855a",
    "regional day off": "#d53f8c",
    "extra day off": "#718096",
}
```

## Running the Application

```bash
cd /PROJECTS/python/rxcalendar
reflex run
```

The app will be available at `http://localhost:3000/` (or next available port).

## Known Limitations

1. **State persistence**: Currently stored in memory; refreshing the page clears all data
2. **Warning message**: Harmless warning about hours handler type (string vs float)
3. **Weekend clicks**: Shows error toast when clicking weekends (by design)

## Future Enhancements

- Add database persistence for data
- Import JSON functionality
- Statistics dashboard (total hours, vacation days, etc.)
- Monthly/weekly summary views
- Print-friendly calendar view
- Multi-year support

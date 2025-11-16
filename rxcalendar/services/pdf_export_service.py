"""PDF calendar export service using reportlab."""

import asyncio
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor


async def generate_calendar_pdf(calendar_data: dict) -> bytes:
    """
    Generate a high-quality PDF document of the calendar in landscape A4 format.
    
    Args:
        calendar_data: Dictionary containing:
            - user_name: str
            - user_role: str
            - division_name: str
            - project_name: str
            - yearly_hours: float
            - yearly_days: float
            - hours_to_days_ratio: float
            - flag_counts: dict[str, int]
            - monthly_data: dict[int, list[dict]] (month -> list of day entries)
            - flag_colors: dict[str, str] (flag -> color hex)
    
    Returns:
        bytes: PDF document data
    """
    # Run the PDF generation in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate_pdf_sync, calendar_data)


def _generate_pdf_sync(calendar_data: dict) -> bytes:
    """Synchronous PDF generation (runs in thread pool)."""
    
    # Create buffer
    buffer = BytesIO()
    
    # Create canvas with A4 landscape
    page_width, page_height = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    
    # Margins
    margin = 0.5 * inch
    
    # Current Y position (PDF coordinates start from bottom-left, so we work downward)
    y = page_height - margin
    
    # ===== HEADER SECTION =====
    # Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(HexColor("#1a202c"))
    title = f"2026 Calendar - {calendar_data['user_name']}"
    c.drawString(margin, y, title)
    y -= 25
    
    # Division and Project
    c.setFont("Helvetica", 10)
    c.setFillColor(HexColor("#2d3748"))
    info_line = f"{calendar_data['division_name']} / {calendar_data['project_name']} / Role: {calendar_data['user_role']}"
    c.drawString(margin, y, info_line)
    y -= 15
    
    # Summary line
    summary_line = f"Yearly Total: {calendar_data['yearly_hours']:.2f}h ({calendar_data['yearly_days']:.2f} days @ {calendar_data['hours_to_days_ratio']}h/day)"
    c.drawString(margin, y, summary_line)
    y -= 20
    
    # Separator line
    c.setStrokeColor(HexColor("#cbd5e0"))
    c.setLineWidth(1)
    c.line(margin, y, page_width - margin, y)
    y -= 15
    
    # ===== CALENDAR GRID (3 rows × 4 columns) =====
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    # Calculate grid dimensions
    cols = 4
    rows = 3
    grid_width = page_width - 2 * margin
    grid_height = y - margin - 80  # Reserve space for footer (in points)
    
    month_width = grid_width / cols
    month_height = grid_height / rows
    
    # Start Y for calendar grid (top of grid)
    grid_start_y = y
    
    for month_idx in range(12):
        row = month_idx // cols
        col = month_idx % cols
        
        month_x = margin + col * month_width
        # In PDF, Y decreases downward, so we subtract from grid_start_y
        month_y = grid_start_y - (row + 1) * month_height
        
        _draw_month_mini_calendar_pdf(
            c,
            month_x,
            month_y,
            month_width - 10,
            month_height - 10,
            month_idx + 1,
            months[month_idx],
            calendar_data.get('monthly_data', {}).get(month_idx + 1, []),
            calendar_data.get('flag_colors', {})
        )
    
    # ===== FOOTER SECTION =====
    footer_y = margin + 70
    
    # Flag legend and counts
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(HexColor("#1a202c"))
    c.drawString(margin, footer_y, "Flag Legend & Counts:")
    footer_y -= 15
    
    flag_info = [
        ("national day off", "#dd6b20"),
        ("Akkodis offered day off", "#3182ce"),
        ("regional day off", "#d53f8c"),
        ("extra day off", "#718096"),
        ("on vacation", "#805ad5"),
    ]
    
    c.setFont("Helvetica", 8)
    legend_x = margin
    for flag_name, color in flag_info:
        count = calendar_data.get('flag_counts', {}).get(flag_name, 0)
        
        # Draw color box
        c.setFillColor(HexColor(color))
        c.setStrokeColor(HexColor("#000000"))
        c.rect(legend_x, footer_y - 8, 10, 10, fill=1, stroke=1)
        
        # Draw label and count
        c.setFillColor(HexColor("#2d3748"))
        label = f"{flag_name}: {count}"
        c.drawString(legend_x + 15, footer_y - 6, label)
        
        legend_x += 200  # Space between legend items
        if legend_x > page_width - margin - 150:
            legend_x = margin
            footer_y -= 15
    
    # Finalize PDF
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()


def _draw_month_mini_calendar_pdf(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    month: int,
    month_name: str,
    entries: list[dict],
    flag_colors: dict[str, str]
):
    """Draw a mini calendar for one month with color-coded entries."""
    
    # Month name at the top (remember Y decreases downward in PDF)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(HexColor("#1a202c"))
    c.drawString(x, y + height - 15, month_name)
    
    # Day headers (M T W T F S S)
    day_headers = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    cell_width = width / 7
    cell_height = (height - 25) / 6  # 6 rows max for a month
    
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(HexColor("#4a5568"))
    header_y = y + height - 30
    for i, day_name in enumerate(day_headers):
        header_x = x + i * cell_width + cell_width / 2 - 3
        c.drawString(header_x, header_y, day_name)
    
    # Get first day of month and number of days
    first_day = datetime(2026, month, 1)
    first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
    
    # Number of days in month
    if month == 12:
        days_in_month = 31
    else:
        try:
            next_month = datetime(2026, month + 1, 1)
            days_in_month = (next_month - first_day).days
        except:
            days_in_month = 31
    
    # Create entries lookup dict
    entries_by_day = {}
    for entry in entries:
        try:
            day = int(entry['date'].split('-')[2])
            entries_by_day[day] = entry
        except:
            continue
    
    # Draw calendar grid (starting from header_y and going down)
    grid_start_y = header_y - 5
    day_num = 1
    
    for week in range(6):
        for weekday in range(7):
            cell_x = x + weekday * cell_width
            cell_y = grid_start_y - (week + 1) * cell_height
            
            # Check if we should draw this day
            if week == 0 and weekday < first_weekday:
                continue  # Empty cell before month starts
            if day_num > days_in_month:
                break  # Month ended
            
            # Get entry for this day
            entry = entries_by_day.get(day_num)
            
            # Determine cell background color
            if entry and entry.get('flag'):
                flag = entry['flag']
                bg_color = flag_colors.get(flag, '#ffffff')
            elif entry and entry.get('hours', 0) > 0:
                bg_color = '#e6ffed'  # Light green for hours
            else:
                bg_color = '#ffffff'
            
            # Draw cell background
            c.setFillColor(HexColor(bg_color))
            c.setStrokeColor(HexColor("#cbd5e0"))
            c.rect(cell_x + 1, cell_y + 1, cell_width - 2, cell_height - 2, fill=1, stroke=1)
            
            # Draw day number
            c.setFont("Helvetica", 6)
            c.setFillColor(HexColor("#1a202c"))
            c.drawString(cell_x + 3, cell_y + cell_height - 8, str(day_num))
            
            # Draw hours if present (and no flag)
            if entry and entry.get('hours', 0) > 0 and not entry.get('flag'):
                hours_text = f"{entry['hours']}h"
                c.setFont("Helvetica", 5)
                c.setFillColor(HexColor("#2d3748"))
                c.drawString(cell_x + 3, cell_y + 3, hours_text)
            
            day_num += 1
        
        if day_num > days_in_month:
            break

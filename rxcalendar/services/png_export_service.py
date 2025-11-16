"""PNG calendar export service using Pillow."""

import asyncio
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


async def generate_calendar_png(calendar_data: dict) -> bytes:
    """
    Generate a high-quality PNG image of the calendar in landscape A4 format.
    
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
        bytes: PNG image data
    """
    # Run the image generation in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _generate_png_sync, calendar_data)


def _generate_png_sync(calendar_data: dict) -> bytes:
    """Synchronous PNG generation (runs in thread pool)."""
    
    # A4 landscape dimensions at 300 DPI for print quality
    dpi = 300
    width_inches = 11.69  # A4 width in landscape
    height_inches = 8.27  # A4 height in landscape
    width = int(width_inches * dpi)
    height = int(height_inches * dpi)
    
    # Create image with white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Font sizes (scaled for 300 DPI)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_header = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
        font_tiny = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        # Fallback to default font if DejaVu not available
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_tiny = ImageFont.load_default()
    
    # Margins
    margin = int(0.5 * dpi)  # 0.5 inch margins
    
    # Current Y position
    y = margin
    
    # ===== HEADER SECTION =====
    # Title
    title = f"2026 Calendar - {calendar_data['user_name']}"
    draw.text((margin, y), title, fill='#1a202c', font=font_title)
    y += 60
    
    # Division and Project
    info_line = f"{calendar_data['division_name']} / {calendar_data['project_name']} / Role: {calendar_data['user_role']}"
    draw.text((margin, y), info_line, fill='#2d3748', font=font_normal)
    y += 40
    
    # Summary line
    summary_line = f"Yearly Total: {calendar_data['yearly_hours']:.2f}h ({calendar_data['yearly_days']:.2f} days @ {calendar_data['hours_to_days_ratio']}h/day)"
    draw.text((margin, y), summary_line, fill='#2d3748', font=font_normal)
    y += 50
    
    # Separator line
    draw.line([(margin, y), (width - margin, y)], fill='#cbd5e0', width=2)
    y += 30
    
    # ===== CALENDAR GRID (3 rows × 4 columns) =====
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    
    # Calculate grid dimensions
    cols = 4
    rows = 3
    grid_width = width - 2 * margin
    grid_height = height - y - margin - 200  # Reserve space for footer
    
    month_width = grid_width // cols
    month_height = grid_height // rows
    
    for month_idx in range(12):
        row = month_idx // cols
        col = month_idx % cols
        
        month_x = margin + col * month_width
        month_y = y + row * month_height
        
        _draw_month_mini_calendar(
            draw,
            month_x,
            month_y,
            month_width - 20,
            month_height - 20,
            month_idx + 1,
            months[month_idx],
            calendar_data.get('monthly_data', {}).get(month_idx + 1, []),
            calendar_data.get('flag_colors', {}),
            font_header,
            font_small,
            font_tiny
        )
    
    # ===== FOOTER SECTION =====
    footer_y = y + grid_height + 30
    
    # Flag legend and counts
    legend_x = margin
    draw.text((legend_x, footer_y), "Flag Legend & Counts:", fill='#1a202c', font=font_normal)
    footer_y += 35
    
    flag_info = [
        ("national day off", "#dd6b20"),
        ("Akkodis offered day off", "#3182ce"),
        ("regional day off", "#d53f8c"),
        ("extra day off", "#718096"),
        ("on vacation", "#805ad5"),
    ]
    
    legend_x = margin
    for flag_name, color in flag_info:
        count = calendar_data.get('flag_counts', {}).get(flag_name, 0)
        
        # Draw color box
        draw.rectangle(
            [(legend_x, footer_y), (legend_x + 30, footer_y + 30)],
            fill=color,
            outline='#000000',
            width=2
        )
        
        # Draw label and count
        label = f"{flag_name}: {count}"
        draw.text((legend_x + 40, footer_y + 5), label, fill='#2d3748', font=font_small)
        
        legend_x += 600  # Space between legend items
        if legend_x > width - margin - 400:
            legend_x = margin
            footer_y += 40
    
    # Convert to bytes
    buffer = BytesIO()
    img.save(buffer, format='PNG', dpi=(dpi, dpi))
    buffer.seek(0)
    return buffer.getvalue()


def _draw_month_mini_calendar(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    month: int,
    month_name: str,
    entries: list[dict],
    flag_colors: dict[str, str],
    font_header,
    font_small,
    font_tiny
):
    """Draw a mini calendar for one month with color-coded entries."""
    
    # Month name
    draw.text((x, y), month_name, fill='#1a202c', font=font_header)
    y += 40
    
    # Day headers (M T W T F S S)
    day_headers = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
    cell_width = width // 7
    cell_height = (height - 40) // 6  # 6 rows max for a month
    
    header_y = y
    for i, day_name in enumerate(day_headers):
        header_x = x + i * cell_width + cell_width // 2 - 10
        draw.text((header_x, header_y), day_name, fill='#4a5568', font=font_small)
    
    y += 30
    
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
    
    # Draw calendar grid
    day_num = 1
    for week in range(6):
        for weekday in range(7):
            cell_x = x + weekday * cell_width
            cell_y = y + week * cell_height
            
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
            draw.rectangle(
                [(cell_x + 2, cell_y + 2), (cell_x + cell_width - 2, cell_y + cell_height - 2)],
                fill=bg_color,
                outline='#cbd5e0',
                width=1
            )
            
            # Draw day number
            day_text = str(day_num)
            draw.text((cell_x + 5, cell_y + 5), day_text, fill='#1a202c', font=font_tiny)
            
            # Draw hours if present (and no flag)
            if entry and entry.get('hours', 0) > 0 and not entry.get('flag'):
                hours_text = f"{entry['hours']}h"
                draw.text((cell_x + 5, cell_y + cell_height - 20), hours_text, fill='#2d3748', font=font_tiny)
            
            day_num += 1
        
        if day_num > days_in_month:
            break

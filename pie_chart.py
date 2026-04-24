import math
import random
from colorama import Fore, Style, init

init(autoreset=True)

#characters are physically taller than they are wide by approximately this ratio
CHAR_HEIGHT_TO_WIDTH_RATIO = 2.0

COLOR_POOL = [
    Fore.LIGHTRED_EX,
    Fore.GREEN,
    Fore.LIGHTYELLOW_EX,
    Fore.LIGHTBLUE_EX,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE,
]

CHAR_POOL = list('+O/#:%\\&*')

DEFAULT_CHART_HEIGHT = 12

def assign_symbols(categories):
    if len(categories) > len(CHAR_POOL):
        raise ValueError('Too many categories for available symbol pool.')
    random.shuffle(CHAR_POOL)
    return {cat: CHAR_POOL[i] for i, cat in enumerate(categories)}

def assign_colors(categories):
    if len(categories) > len(COLOR_POOL):
        raise ValueError('Too many categories for available color pool.')
    random.shuffle(COLOR_POOL)
    return {cat: COLOR_POOL[i] for i, cat in enumerate(categories)}

def compute_segments(data):
    total = sum(data.values())
    if total <= 0:
        raise ValueError('Total of values must be greater than zero.')

    segments = []
    current_angle = 0.0

    #produce a list of angle cutoffs per category
    for category, value in data.items():
        angle = (value / total) * 2 * math.pi
        segments.append((category, current_angle, current_angle + angle))
        current_angle += angle
    return segments

def angle_at_point(x, y):
    angle = math.atan2(y, x)
    return angle if angle >= 0.0 else angle + 2 * math.pi

def category_for_angle(angle, segments):
    if not segments: raise ValueError('No segments by which to assign category')
    for cat, start, end in segments:
        if start <= angle < end:
            return cat

#given data, a dictionary of categories to obeservances,
#draw a pie chart of the given height
#return the chart as a string
def generate_pie_chart(title, data, height, use_color=False):

    width = int(round(height * CHAR_HEIGHT_TO_WIDTH_RATIO))
    if width < 3 or height < 3:
        raise ValueError('Width and height must be at least 3.')

    categories = list(data.keys())
    symbols = assign_symbols(categories)
    colors = assign_colors(categories) if use_color else {}

    no_data = False
    try: segments = compute_segments(data)
    except ValueError: no_data = True

    cx = width / 2
    cy = height / 2
    #radius = min(width, height) / 2 - 0.5

    rows = []

    for j in range(height):
        row_chars = []
        for i in range(width):
            #normalize coordinates; width is usually greater than height, since we are
            #correcting using CHAR_HEIGHT_TO_WIDTH_RATIO, but the circle should be drawn
            #to fill the height and width, so calculate these elliptic coordinates to use
            nx = (i + 0.5 - cx) / (width / 2)
            ny = (j + 0.5 - cy) / (height / 2)

            #make the chart empty by falsifying this if-statemet when no data are supplied
            if nx * nx + ny * ny <= 1.0 * (-1.0 if no_data else 1.0):
                angle = angle_at_point(nx, ny)
                cat = category_for_angle(angle, segments)
                ch = symbols[cat]
                if use_color: ch = f'{colors[cat]}{ch}{Style.RESET_ALL}'
                row_chars.append(ch)
            else:
                row_chars.append(' ')
        rows.append(''.join(row_chars))

    # Build legend
    total = sum(data.values())
    legend_lines = []

    for cat in categories:
        value = data[cat]
        pct = 'N/A' if no_data else int(round((value / (total)) * 100))
        symbol = symbols[cat]

        symbol_display = f'{colors[cat]}{symbol}{Style.RESET_ALL}' if use_color else symbol

        legend_lines.append(f'{symbol_display} = {cat} ({value}, {pct}%)')

    #add border about pie and legend to the side
    legend_start_line = len(rows) // 2 - len(legend_lines) // 2
    border = '+' + '-' * (width) + '+'
    rows = [border] + [f'|{row}|' for row in rows] + [border]
    for i, legend_line in enumerate(legend_lines):
        rows[i + legend_start_line] += '  ' + legend_line

    #add title
    title_padding = ' ' * ((len(rows[0]) - len(title)) // 2)
    title_row = title_padding + title + title_padding

    return '\n'.join([title_row] + rows)


# Example usage
def example_chart():
	data = {
		'Peanuts': 5,
		'Walnuts': 18,
		'Almonds': 10,
		'Cashews': 2,
		'Pecans' : 7,
	}

	chart = generate_pie_chart('Nut', data, height=12, use_color=False)
	print(chart)

if __name__ == '__main__' : example_chart()

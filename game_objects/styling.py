from collections import defaultdict

from colorama import Fore, Back, Style

from game_objects.color import Color, generate_color


#Color.render exposed as a standalone printing function
#(an unbound method is just a function: (color, text, deterministic))
style_text = Color.render

#color picker for generating different-colored prompts
prompt_generator = generate_color()

SUSPICION_STYLE = defaultdict(lambda: f'{Back.LIGHTWHITE_EX}{Fore.BLACK}') | {
    Color.BLUE:       Back.BLUE,
    Color.RED:        Back.RED,
    Color.YELLOW:     f'{Back.LIGHTYELLOW_EX}{Fore.BLACK}',
    Color.WHITE:      f'{Back.LIGHTWHITE_EX}{Fore.BLACK}',
    Color.GREEN:      Back.GREEN,
    Color.MULTICOLOR: Back.MAGENTA
}

def guess_text(color, text):
    """
    color: a Color object
    text: arbitrary text to be colored
    """
    return f'{SUSPICION_STYLE[color]}{text}{Style.RESET_ALL}'

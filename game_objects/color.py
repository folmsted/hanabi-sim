from enum import Enum, nonmember
from colorama import Fore, Back, Style
from collections import defaultdict
import random

class Color(Enum):
    BLUE = 1
    GREEN = 2
    RED = 3
    WHITE = 4
    YELLOW = 5
    MULTICOLOR = 6
    
    #A generator to randomly shuffle some reasonably legible colors and
    #return them in that order forever, repeating when exhausted.
    def generate_color():
        #Commented colors are harder to read; move pound signs to include additional colors 
        colors =  ([
                      Fore.RED, Fore.GREEN, Fore.YELLOW, #Fore.BLACK,
                      Fore.MAGENTA, Fore.CYAN, #Fore.WHITE,
                      Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, #Fore.LIGHTBLACK_EX
                      Fore.LIGHTYELLOW_EX, Fore.LIGHTBLUE_EX,
                      Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, #Fore.LIGHTWHITE_EX
                  ])
        random.shuffle(colors)
        colors.pop() # delete one at random for a little variety

        i = 0
        while (i < len(colors)):
            yield colors[i]
            i = (i + 1) % len(colors)

    #color picker for generating different-colored prompts
    prompt_generator = nonmember(generate_color())
    #color picker for spelling "MULTICOLOR" in rainbow letters
    multicolor_generator = nonmember(generate_color())

    def __str__(self):
        return style_text(self, self.name)

PRINT_STYLE = {
    Color.BLUE:       Fore.LIGHTBLUE_EX,
    Color.RED:        Fore.LIGHTRED_EX,
    Color.YELLOW:     Fore.LIGHTYELLOW_EX,
    Color.WHITE:      Fore.LIGHTWHITE_EX,
    Color.GREEN:      Fore.GREEN,
    Color.MULTICOLOR: Fore.MAGENTA
}

SUSPICION_STYLE = defaultdict(lambda: f'{Back.LIGHTWHITE_EX}{Fore.BLACK}') | {
    Color.BLUE:       Back.BLUE, 
    Color.RED:        Back.RED,
    Color.YELLOW:     f'{Back.LIGHTYELLOW_EX}{Fore.BLACK}',
    Color.WHITE:      f'{Back.LIGHTWHITE_EX}{Fore.BLACK}',
    Color.GREEN:      Back.GREEN,
    Color.MULTICOLOR: Back.MAGENTA
}

def style_text(color, text, deterministic = False):
    """
    color: a Color object or a valid colorama color
    text: arbitrary text to be colored
    """
    match color:
        case Color.MULTICOLOR if not deterministic:
            colored_characters = [next(Color.multicolor_generator) + c for c in text]
            return f'{"".join(colored_characters)}{Style.RESET_ALL}'
        case Color():
            return f'{PRINT_STYLE[color]}{text}{Style.RESET_ALL}'
        case _:
            return f'{color}{text}{Style.RESET_ALL}'

def guess_text(color, text):
    """
    color: a Color object
    text: arbitrary text to be colored
    """
    return f'{SUSPICION_STYLE[color]}{text}{Style.RESET_ALL}'


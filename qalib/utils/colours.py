from discord import Colour


COLOURS = {'teal': 0x1abc9c,
           'dark_teal': 0x11806a,
           'green': 0x2ecc71,
           'dark_green': 0x1f8b4c,
           'blue': 0x3498db,
           'dark_blue': 0x206694,
           'purple': 0x9b59b6,
           'dark_purple': 0x71368a,
           'magenta': 0xe91e63,
           'dark_magenta': 0xad1457,
           'gold': 0xf1c40f,
           'dark_gold': 0xc27c0e,
           'orange': 0xe67e22,
           'dark_orange': 0xa84300,
           'red': 0xe74c3c,
           'dark_red': 0x992d22,
           'lighter_grey': 0x95a5a6,
           'dark_grey': 0x607d8b,
           'light_grey': 0x979c9f,
           'darker_grey': 0x546e7a,
           'blurple': 0x7289da,
           'greyple': 0x99aab5}


def get_colour(colour) -> Colour:
    """maps the name of the a colour to its value
    Args:
        colour (str): the name of the colour, or it's rgb components.
    Returns:
        int: hexadecimal value of the colour.
    """
    if colour.replace(' ', '_') in COLOURS:
        return COLOURS[colour.replace(' ', '_')]
    colour = colour.split(',')
    colour = map(int, colour)
    return Colour.from_rgb(*colour)

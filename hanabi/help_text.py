#help strings.  Moved here because they are unruly and ugly
help_play = \
    'The "play" command, short form "p".  '\
    'Used to indicate that turn player should play a card.\n'\
    'Usage:\n'\
    'play <position> <card>\n'\
    'This causes the turn player to play his card in position <position> of his hand.\n'\
    '---> <card> is a value which indicates what value the card had on being revealed.\n'\
    '---> <card> is formatted as <color><number> or <number><color>; '\
    'one-letter abbreviations allowed.\n'\
    'Examples:\n'\
    'play 1 1y (player plays card in position 1, which was a yellow 1)\n'\
    'play 5 3green (player plays card in position 3, which was a green 3)\n'\
    'play 2 r1 (player plays card in position 2, which was a red 1)'

help_hint = \
    'The "hint" command, short form "h".  Used to indicate\n'\
    'that the turn player should give a hint to another player.\n'\
    'Usage:\n'\
    'hint <player> <positions> <hint>\n'\
    'This causes the hand of <player> to be updated '\
    'according to the <hint> for <positions>.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <positions> is a space-separated list of numbers\n'\
    '     indicating the postions at which to apply the <hint>.\n'\
    '---> <hint> is a number or a string (not both) representing\n'\
    '     the color or number being indicated.\n'\
    'Examples:\n'\
    'hint 1 1 3 4 r (player 1 has red cards at positions 1, 3, 4)\n'\
    'hint fra 2 5 (the player whose name starts "fra" has a 5 at position 2)\n'\
    'hint janos 1 2 3 red (player janos has red cards at positions 1, 2, 3)\n'\
    'hint 2 4 5 2 (player 2 has a two card at positions 4, 5)'

help_discard = \
    'The "discard" command, short form "d".  Used to '\
    'indicate that turn player should discard a card.\n'\
    'Usage:\n'\
    'discard <position> <card>\n'\
    'This causes the turn player to discard his card '\
    'in position <position> of his hand.\n'\
    '---> <card> is a value which indicates what value the card had on being revealed.\n'\
    '---> <card> is formatted as <color><number> or '\
    '<number><color>; abbreviations allowed.\n'\
    'Examples:\n'\
    'discard 1 1y (player discards card in position 1, which was a yellow 1)\n'\
    'discard 5 3green (player discards card in position 3, which was a green 3)\n'\
    'discard 2 r1 (player discards card in position 2, which was a red 1)'

help_guess = \
    'The "guess" command, short form "g".  Used to '\
    'guess the number or color or a card.\n'\
    'Usage:\n'\
    'guess <player> <position> <guess>\n'\
    'This causes the card at <position> in the hand of <player> to be '\
    'updated according to <guess>.\n'\
    'Note that this does not advance play; it is just '\
    'a way to keep track of thoughts.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <position> is a number indicating the postion \n'\
    '     at which to apply <guess>.\n'\
    '---> <guess> is a number or a string (not both) '\
    'representing the color or number being indicated.\n'\
    'Examples:\n'\
    'guess 1 4 g (player 1 guesses a green card is at position 4)\n'\
    'guess jim 2 5 (the player whose name starts "jim" guesses a 5 is at position 2)\n'\
    'guess janos 3 red (player janos guesses a red card is at position 3)\n'\
    'guess 0 1 2 (player 0 guesses a 2 is at position 1)'

help_undo = \
    'The "undo" command, short form "u".  Used to revert to the previous game state.\n'\
    'Usage:\n'\
    'undo'

help_swap = \
    'The "swap" command (no short form).  Used to '\
    'swap the positions of two cards in a player\'s hand.\n'\
    'Usage:\n'\
    'swap <player> <position1> <position2>\n'\
    'This causes the card at position <position1> to be placed into <position2>.\n'\
    ' and the card in <position2> to be placed in <position1>\n'\
    'Note that this does not advance play; it just '\
    'changes the order of cards in the hand.\n'\
    '---> <player> can be a number indicating turn order or a\n'\
    '     string which unambiguously identifies the player by name.\n'\
    '---> <position1> and <position2> are integers indicating\n'\
    '     the positions of the cards to swap.\n'\
    'Examples:\n'\
    'swap 1 4 5 (player 1 swaps the cards at positions 4 and 5)\n'\
    'swap sigismund 2 5 (the player whose name starts "sigismund" '\
    'swaps the cards at positions 2 and 5)'

help_quit = \
    'The "quit" command, short form "q".  Used to quit the simulation.\n'\
    'Usage:\n'\
    'quit'

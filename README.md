# hanabi-sim
A simulator which tracks the publicly available information in a game of Hanabi.

This is not an _implementation_ of Hanabi; it does not allow you to play.  Rather, it tracks the information which has been made public to all players in a game which is being played, given the actions taken thus far in the game.  It allows for easy recollection of the information one has been given about one's hand (or the information others have been given about theirs), the current list of cards not accounted for in public places (discards, started fireworks), and a few other things.

Usage:

`python3 hanabi_sim.py [options]`

You can specify `-o <outfile>` to record the commands to a file.  Similarly, use `-i <infile>` to load the commands from a file.  There is a `-v` option which causes hanabi-sim to automatically print the hand of the relevant player after an action is taken.

This will drop the user into a cli-like tool which will allow him to specify the players (in order) and their preferred mode of hand management (how is a card replaced when it is played: is the card inserted at the right, shifting other cards left or on the right, shifting other cards left; or is the card inserted in the place of the old card).  After players are established, the user inputs the hints, plays, and discards of the Hanabi game into the program, or queries it for information.  A few examples:

h 1 3 4 b (the turn player gives a hint to player 1 that his 3 and 4 positions are blue)

p 3 1yellow (the turn player plays his card at position 3, which turned out to be a yellow 1)

d 1 5r (the turn player discards his card at position 1, which turned out to be the red 5)

Note that by convention, players are numbered 1, ..., n (not 0, ... n - 1) and that cards in a player's hand are numbered 1, ..., n from left to right, _from that player's perspective_.  So your card at position 1 is your leftmost card.  If you hold 5 cards, your position 5 card is your rightmost.

Written and tested (to the extent it is tested) on Python 3.13.5



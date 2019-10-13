# Coup Game IA

This repository gathers a COUP game API and some experiments on artificial intelligence able to play this game.

## Getting started

A demo script is available in `play.py`. It will play 1000 games with four players:
- A dumb player, choosing randomly its action based on a lying and accusing probability
- A smart player, simulating 100 games at each epoch in a Monte-Carlo style, and trying to predict the state in 2 epochs
- A super smart player, simulating 300 games and predicting the state in 5 epochs
- An anti-smart player, simulating 100 games and minimizing its chances of winning

The result after 1000 games is always the same: the super-smart player wins (35%), followed by the smart player (30%), the dumb player (20%) and finally the anti-smart one (15%)

Note that you can also setup a "true" player which will ask you what to do

## Contributing

If you wish to contribute here are a few things you could do:
- adding new cards / actions and making stats on different game configurations
- creating new player AI and trying to beat the "smart" one

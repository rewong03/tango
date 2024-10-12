# Tango 🕺🕺

This is the clone of the Tango game on [Linkedin](https://www.linkedin.com/games/tango/) that lets you play on demand, since my sun (girlfriend) and I hate waiting until 2am CST for a new board to come out.

Install the game with the following command:
```
pip install -r requirements.txt
```

Run the game with the following command:
```
python3 tango.py
```

## Controls
- Left click to toggle between placing a sun, moon, or clearing a square
- Right click to place a question sun, question moon, or clearing a square (for when you're unsure of a square)
- Click "New Game" for a new board
- Click "Clear Board" to reset the board to the initial state
- Click "Get a Hint!" to reveal a square
- Click on "Give Up :(" if you suck (jk)

## Board Generation
- Boards are *guaranteed* to have exactly one solution (to the best of my knowledge)
- Boards are also *guaranteed* to be solvable without any need to guess (to the best of my knowledge)

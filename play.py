from collections import defaultdict

from tqdm import trange

from coup.game import *

if __name__ == '__main__':
    winners = defaultdict(lambda: 0)
    r = trange(1000)
    for _ in r:
        players = [
            DumbPlayer('dumb'),
            SmartPlayer('smart'),
            SmartPlayer('super-smart', n_simulations=300, n_epochs=5),
            AntiSmartPlayer('anti-smart'),
        ]
        G = CoupGame(players, verbose=False)
        G.epochs(100)
        if G.winner is not None: winners[G.winner.nickname] += 1
        r.set_postfix(winners)
    print(winners)

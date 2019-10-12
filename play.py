import pandas as pd
from matplotlib import pyplot as plt
from tqdm import trange

from coup.game import *


if __name__ == '__main__':
    winners = []
    for _ in trange(1000):
        G = CoupGame(['dumb', 'dumb', 'dumb', 'smart'], verbose=False)
        G.epochs(100)
        winners.append(G.winner.nickname)
    print('')
    for n in set(winners):
        print('%s: %d' % (n, sum(1 for w in winners if w == n)))


    # stats = dict(other_p_lying=[], other_p_accusing=[], p_lying=[], p_accusing=[])
    # Gref = CoupGame(4)
    # Nsim = 1000
    # Gsim = [SimulatedGame(Gref, Gref.players[0]) for _ in range(Nsim)]
    # for _ in range(50):
    #     if not Gref.epoch():
    #         break
    #     Gsim = [g for g in Gsim if g.epoch() and g.like(Gref)]
    #     print('%d games removed' % (Nsim - len(Gsim)))
    #     while len(Gsim) < Nsim:
    #         Gsim.append(SimulatedGame(Gref, Gref.players[0]))

    #
    # # Gref = CoupGame(4)
    # # GG = SimulatedGame()
    # for _ in trange(1000):
    #     random.seed()
    #     # G = GG.clone()
    #     G = CoupGame(4, true_player=True)
    #     for i in range(200):
    #         if not G.epoch():
    #             break
    #     if G.winner is None:
    #         continue
    #     stats['other_p_lying'].append(np.mean([p.p_lying for p in G.players if p != G.winner]))
    #     stats['other_p_accusing'].append(np.mean([p.p_accusing for p in G.players if p != G.winner]))
    #     stats['p_lying'].append(G.winner.p_lying)
    #     stats['p_accusing'].append(G.winner.p_accusing)
    #
    # df = pd.DataFrame(stats)
    # df.plot.scatter('other_p_lying', 'p_accusing')
    # df.plot.scatter('other_p_accusing', 'p_lying')
    # plt.show()

import pandas as pd
from matplotlib import pyplot as plt
from tqdm import trange

from coup.player import *


class Game:
    def __init__(self, players, verbose=True):
        self.players = players
        self.next_player = players[random.randint(0, len(self.players)-1)] if self.players else None
        self.verbose = verbose
        self.epochs = 0

    def kill(self, player):
        card = player.choose_kill()
        if card is not None:
            card.dead = True
        if self.verbose: print('%s got killed: %s' % (player, player._cards))

    def epoch(self):
        if self.winner is not None:
            return False

        if self.verbose: print('\n---------\nEpoch #%d - %s / %s / treasure: %d' % (self.epochs, self.next_player, self.next_player._cards, self.next_player.treasure))
        action = self.next_player.act()
        assert action.can()
        if self.verbose: print(action)
        self.next_player.pay(action.__cost__)

        other_players = [action.other] if isinstance(action, DirectAction) else [p for p in self.players if p != self.next_player and p.alive]

        if action.__card_category__ is not None:
            random.shuffle(other_players)
            for accuser in other_players:
                if accuser.accuse(self.next_player, action):
                    if self.verbose: print('%s accuses %s of lying' % (accuser, self.next_player))
                    c = action.truly_can()
                    if c:
                        self.kill(accuser)
                        self.next_player.exchange_card(c[0])
                    else:
                        self.kill(self.next_player)
                        action.blocked = True
                    break

        if not action.blocked:
            other_players = [p for p in other_players if p.alive]
            random.shuffle(other_players)
            for blocker in other_players:
                block = blocker.block(action, self.next_player)
                if block is not None:
                    if self.verbose: print(block)
                    if self.next_player.accuse(block, blocker):
                        if self.verbose: print('%s accuses %s of lying' % (self.next_player, blocker))
                        c = block.truly_can()
                        if c:
                            action.blocked = True
                            self.kill(self.next_player)
                            blocker.exchange_card(c[0])
                            break
                        else:
                            self.kill(blocker)
                            block.blocked = True
                            continue
                    else:
                        action.blocked = True
                        break

        if not action.blocked:
            action.do(self)

        self.epochs += 1
        i = self.players.index(self.next_player)
        next_player = None
        while next_player is None or not next_player.alive:
            i = (i + 1) % len(self.players)
            next_player = self.players[i]
            if next_player == self.next_player:
                return False
        self.next_player = next_player
        return True

    @property
    def winner(self):
        p = [p for p in self.players if p.alive]
        return p[0] if len(p) == 1 else None


class CoupGame(Game):

    def __init__(self, n_players, verbose=False, true_player=False):
        self.middle = MiddleCardSet()
        players = [TruePlayer('you', self)] if true_player else []
        while len(players) < n_players:
            players.append(DumbPlayer('player%d' % len(players), self))
        for _ in range(2):
            for p in players:
                if len(p._cards) < 2:
                    p.pick_card(self.middle)
        super().__init__(players, verbose)


class SimulatedGame(Game):
    __player_class__ = DumbPlayer

    def __init__(self, game, pov_player):
        self.middle = MiddleCardSet()
        players = [DumbPlayer(p.nickname, self) for p in game.players]
        self.pov_player = [p for p in players if p == pov_player][0]
        for p in players:
            for c in p._cards:
                if p == pov_player or c.dead:
                    p.pick_card(self.middle, c.__nickname__)
        super().__init__(players, verbose=False)

    def clone(self):
        return self.__class__(self, self.pov_player)


if __name__ == '__main__':
    stats = dict(other_p_lying=[], other_p_accusing=[], p_lying=[], p_accusing=[])
    Gref = CoupGame(4)
    GG = SimulatedGame(4)
    for _ in trange(1000):
        random.seed()
        G = GG.clone()
        for i in range(200):
            if not G.epoch():
                break
        if G.winner is None:
            continue
        stats['other_p_lying'].append(np.mean([p.p_lying for p in G.players if p != G.winner]))
        stats['other_p_accusing'].append(np.mean([p.p_accusing for p in G.players if p != G.winner]))
        stats['p_lying'].append(G.winner.p_lying)
        stats['p_accusing'].append(G.winner.p_accusing)

    df = pd.DataFrame(stats)
    df.plot.scatter('other_p_lying', 'p_accusing')
    df.plot.scatter('other_p_accusing', 'p_lying')
    plt.show()

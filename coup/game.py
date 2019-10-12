from coup.player import *


class Game:
    def __init__(self, players, verbose=True):
        self.middle = MiddleCardSet()
        self.players = players
        self.next_player = players[random.randint(0, len(self.players)-1)] if self.players else None
        self.verbose = verbose
        self.n_epochs = 0
        self.draw_cards()

    def draw_cards(self):
        for _ in range(2):
            for p in self.players:
                if len(p._cards) < 2:
                    p.pick_card(self.middle)

    def kill(self, player):
        card = player.choose_kill()
        if card is not None:
            card.dead = True
        if self.verbose: print('%s got killed: %s' % (player, player._cards))

    def __repr__(self):
        return 'Epoch #%d / %s' % (self.n_epochs, ' / '.join(
            '%s - %d - %s' % (str(p), p._treasure, ' '.join(map(str, p._cards))) for p in self.players
        ))

    def epoch(self):
        assert self.next_player.alive
        if self.winner is not None:
            return True

        for p in self.players:
            p.epoch()

        if self.verbose: print('\n---------\nEpoch #%d - %s / %s / treasure: %d' % (self.n_epochs, self.next_player, self.next_player._cards, self.next_player.treasure))
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

        self.n_epochs += 1
        i = self.players.index(self.next_player)
        next_player = None
        while next_player is None or not next_player.alive:
            i = (i + 1) % len(self.players)
            next_player = self.players[i]
            if next_player == self.next_player:
                return False
        assert next_player.alive
        self.next_player = next_player
        return True

    def epochs(self, n=200):
        for _ in range(n):
            if not self.epoch():
                break
        return self.winner

    @property
    def alive_players(self):
        return [p for p in self.players if p.alive]

    @property
    def winner(self):
        return self.alive_players[0] if len(self.alive_players) == 1 else None

    def get_card_set(self, card_set):
        if isinstance(card_set, MiddleCardSet) or card_set == 'middle':
            return self.middle
        if isinstance(card_set, Player):
            card_set = card_set.nickname
        if not isinstance(card_set, str):
            raise TypeError(card_set)
        return [p for p in self.players if p.nickname == card_set][0]


class CoupGame(Game):

    def __init__(self, players, verbose=False, true_player=False):
        self.middle = MiddleCardSet()
        if isinstance(players, int): players = ['dumb'] * players
        players = [PLAYER_TYPE[p]('%s%d' % (p, i+1), self) for i, p in enumerate(players)]
        super().__init__(players, verbose or true_player)


class SimulatedGame(Game):
    __player_class__ = DumbPlayer

    def __init__(self, game, pov_player=None):
        self.middle = MiddleCardSet()
        self.players = [DumbPlayer(p.nickname, self) for p in game.players]
        self.pov_player_nickname = game.pov_player_nickname if isinstance(game, SimulatedGame) else pov_player.nickname
        for new_player, old_player in zip(self.players, game.players):
            new_player._treasure = old_player.treasure
            for c in old_player._cards:
                if new_player == self.pov_player_nickname or c.dead:
                    new_player.pick_card(self.middle, c.__nickname__).dead = c.dead
        self.verbose = False
        self.next_player = [p for p in self.players if p.nickname == game.next_player.nickname][0]
        self.n_epochs = game.n_epochs
        self.draw_cards()

    def like(self, other):
        if not isinstance(other, Game):
            print(other.__class__)
            print(CoupGame)
            assert other.__class__ == CoupGame
            raise TypeError(other)
        assert len(self.players) == len(other.players)
        for player, other_player in zip(self.players, other.players):
            assert player.nickname == other_player.nickname
            if player.treasure != other_player.treasure: return False
            if player.alive != other_player.alive: return False
            assert len(player._cards) == len(other_player._cards)
            for card, other_card in zip(player._cards, other_player._cards):
                if card.dead != other_card.dead: return False
                if player == self.pov_player_nickname or card.dead:
                    if card.__nickname__ != other_card.__nickname__: return False
        return True

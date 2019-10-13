from coup.player import *


class Game:
    def __init__(self, players, verbose=True):
        self.middle = MiddleCardSet()
        self.players = players
        for p in players:
            p.game = self
        self.next_player = players[random.randint(0, len(self.players)-1)] if self.players else None
        self.verbose = verbose
        self.n_epochs = 0
        self.draw_player_cards()

    def get_player(self, nickname):
        return [p for p in self.players if p.nickname == nickname][0]

    def draw_player_cards(self):
        for _ in range(2):
            for p in self.players:
                if len(p.cards) < 2:
                    p.pick_card(self.middle)

    def kill(self, player):
        if not player.alive:
            return
        player.choose_kill().dead = True
        if self.verbose: print('%s got killed: %s' % (player, player.cards))

    def __repr__(self):
        return 'Epoch #%d / %s' % (self.n_epochs, ' / '.join(
            '%s - %d - %s' % (str(p), p._treasure, ' '.join(map(str, p.cards))) for p in self.players
        ))

    def epoch(self, action=None):
        if not self.next_player.alive or self.winner is not None:
            return self

        for p in self.players:
            p.epoch()

        if self.verbose: print('\n---------\nEpoch #%d - %s / %s / treasure: %d' % (self.n_epochs, self.next_player, self.next_player.cards, self.next_player.treasure))
        if action is None:
            action = self.next_player.act()
        assert action.can(self)
        if self.verbose: print(action)
        self.next_player.pay(action.__cost__)

        blocked = False
        if action.__card_category__ is not None:
            players = self.players.copy()
            random.shuffle(players)
            for accuser in players:
                if accuser.nickname == self.next_player.nickname:
                    continue
                if accuser.accuse(self.next_player, action):
                    if self.verbose: print('%s accuses %s of lying' % (accuser, self.next_player))
                    c = action.truly_can(self)
                    if c:
                        self.kill(accuser)
                        self.next_player.exchange_card(c[0])
                    else:
                        self.kill(self.next_player)
                        blocked = True
                    break

        if not blocked:
            players = [p for p in self.players if p.alive]
            random.shuffle(players)
            for blocker in players:
                if blocker.nickname == self.next_player.nickname:
                    continue
                block = blocker.block(action, self.next_player)
                if block is not None:
                    if self.verbose: print(block)
                    if self.next_player.accuse(block, blocker):
                        if self.verbose: print('%s accuses %s of lying' % (self.next_player, blocker))
                        c = block.truly_can(self)
                        if c:
                            blocked = True
                            self.kill(self.next_player)
                            blocker.exchange_card(c[0])
                            break
                        else:
                            self.kill(blocker)
                            continue
                    else:
                        blocked = True
                        break

        if not blocked:
            action.do(self)

        self.n_epochs += 1
        i = self.players.index(self.next_player)
        next_player = None
        while next_player is None or not next_player.alive:
            i = (i + 1) % len(self.players)
            next_player = self.players[i]
            if next_player == self.next_player:
                return self
        assert next_player.alive
        self.next_player = next_player
        return self

    def epochs(self, n=200):
        for _ in range(n):
            self.epoch()
            if self.winner is not None:
                break
        return self

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
        players = [PLAYER_TYPE[p]('%s%d' % (p, i+1), self) if isinstance(p, str) else p for i, p in enumerate(players)]
        super().__init__(players, verbose or true_player)


class SimulatedGame(Game):
    __player_class__ = DumbPlayer

    def __init__(self, game, pov_player=None):
        self.middle = MiddleCardSet()
        self.players = [DumbPlayer(p.nickname, self) for p in game.players]
        self.pov_player_nickname = game.pov_player_nickname if isinstance(game, SimulatedGame) else pov_player.nickname
        for new_player, old_player in zip(self.players, game.players):
            new_player._treasure = old_player.treasure
            for c in old_player.cards:
                if new_player == self.pov_player_nickname or c.dead:
                    new_player.pick_card(self.middle, c.__nickname__).dead = c.dead
        self.verbose = False
        self.next_player = [p for p in self.players if p.nickname == game.next_player.nickname][0]
        self.n_epochs = game.n_epochs
        self.draw_player_cards()

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
            assert len(player.cards) == len(other_player.cards)
            for card, other_card in zip(player.cards, other_player.cards):
                if card.dead != other_card.dead: return False
                if player == self.pov_player_nickname or card.dead:
                    if card.__nickname__ != other_card.__nickname__: return False
        return True

import numpy as np

from coup.action import *


class Player(CardSet):
    def __init__(self, nickname=None, game=None):
        super().__init__()
        self.nickname = nickname
        self._treasure = 2
        self.game = game

    def exchange_card(self, card):
        assert not card.dead
        self.game.middle.pick_card(self, card)
        self.pick_card(self.game.middle)

    @property
    def treasure(self):
        return self._treasure

    def pay(self, n):
        if not n:
            return
        assert self._treasure >= n
        self._treasure -= n

    def income(self, n):
        if not n:
            return
        self._treasure += n

    @property
    def alive(self):
        return any(not c.dead for c in self.cards)

    def __str__(self):
        return self.nickname

    def clone(self):
        p = super(Player, self).clone()
        p.nickname = self.nickname
        p._treasure = self._treasure
        return p

    def _possible_actions(self, game=None):
        game = self.game if game is None else game
        other_players = [p for p in game.players if p.alive and p != self]
        actions = [A(self) for A in ACTIONS if issubclass(A, SimpleAction)]
        actions += [A(self, other_player) for A in ACTIONS if issubclass(A, DirectAction) for other_player in other_players]
        actions = [a for a in actions if a.can(self.game)]
        return actions

    def act(self):
        raise NotImplementedError

    def block(self, action, other):
        raise NotImplementedError

    def accuse(self, action, other):
        raise NotImplementedError

    def learn_card(self, card, set):
        raise NotImplementedError

    # def learn_action(self, action):
    #     raise NotImplementedError

    def choose_kill(self):
        raise NotImplementedError

    def choose_look(self):
        raise NotImplementedError

    def epoch(self):
        pass

    # def __eq__(self, other):
    #     if isinstance(other, Player):
    #         return self.nickname == other.nickname
    #     elif isinstance(other, str):
    #         return self.nickname == other
    #     else:
    #         raise TypeError(other)


class TruePlayer(Player):
    def __init__(self, nickname=None, game=None):
        nickname = 'you'
        super().__init__(nickname, game)

    def act(self):
        print('Your turn!')
        print('Your cards: %s' % ' '.join([c.__nickname__.title() for c in self.cards if not c.dead]))
        actions = self._possible_actions()
        print('Your possible actions:\n%s' % '\n'.join(' %d: %s' % (i, str(a)) for i, a in enumerate(actions)))
        return actions[int(input('Your choice? '))]

    def block(self, action, other):
        actions = [BA(self, other, action) for BA in ACTIONS if issubclass(BA, BlockAction)]
        actions = [ba for ba in actions if ba.can()]
        if not actions:
            return None
        actions = ['nothing'] + actions
        print('Your turn to block!')
        print('Your cards: %s' % ' '.join([c.__nickname__.title() for c in self.cards if not c.dead]))
        print('Your possible blocking actions:\n%s' % '\n'.join(' %d: %s' % (i, str(a)) for i, a in enumerate(actions)))
        return actions[int(input('Your choice? '))]

    def accuse(self, action, other):
        return input('Accuse lying? (y/n) ') in ('y', 'Y')

    def choose_kill(self):
        print('Your got killed!')
        cards = [c for c in self.cards if not c.dead]
        if len(cards) == 1:
            return cards[0]
        elif len(cards) == 0:
            return None
        print('Your cards:\n%s' % '\n'.join([' %d: %s' % (i, c.__nickname__.title()) for i, c in enumerate(self.cards)]))
        return cards[int(input('Your choice? '))]

    def learn_card(self, card, set):
        print('%s in %s' % (card, set))

    def learn_action(self, action):
        print(str(action))

    def choose_look(self):
        print('Your got looked!')
        cards = [c for c in self.cards if not c.dead]
        if len(cards) == 1:
            return cards[0]
        print('Your cards:\n%s' % '\n'.join([' %d: %s' % (i, c.__nickname__.title()) for i, c in enumerate(self.cards)]))
        return cards[int(input('Your choice? '))]


class DumbPlayer(Player):
    def __init__(self, nickname=None, game=None):
        super().__init__(nickname, game)
        self.p_lying = np.random.normal(.5, .2)
        self.p_accusing = np.random.normal(.5, .2)

    def choose_kill(self):
        self.shuffle()
        cards = [c for c in self.cards if not c.dead]
        return cards[0] if len(cards) else None

    def act(self):
        actions = self._possible_actions()
        actions = [a for a in actions if a.truly_can() or random.random() > self.p_lying / len(actions)]
        random.shuffle(actions)
        return actions[0]

    def accuse(self, action, other):
        return random.random() < self.p_accusing

    def block(self, action, other):
        actions = [BA(self, other, action) for BA in ACTIONS if issubclass(BA, BlockAction)]
        actions = [ba for ba in actions if ba.can()]
        actions = [ba for ba in actions if ba.truly_can() or random.random() > self.p_lying / len(actions)]
        random.shuffle(actions)
        return actions[0] if actions else None

    def learn_card(self, card, set):
        pass

    def choose_look(self):
        self.shuffle()
        return [c for c in self.cards if not c.dead]

    def __repr__(self):
        return '%s (%s)' % (
            self.__class__.__name__,
            ' '.join('%s=%s' % x for x in dict(
                nickname=self.nickname,
                lying=round(self.p_lying, 2),
                accusing=round(self.p_accusing, 2),
            ).items())
        )


class SmartPlayer(DumbPlayer):
    def __init__(self, nickname=None, game=None, n_simulations=100, n_epochs=2):
        super().__init__(nickname, game)
        self.simulations = []
        self.n_simulations = n_simulations
        self.n_epochs = n_epochs

    def populate_simulations(self):
        from coup.game import SimulatedGame
        while len(self.simulations) < self.n_simulations:
            self.simulations.append(SimulatedGame(random.choice(self.simulations + [self.game]), self))

    def learn_card(self, card, set):
        self.simulations = [g for g in self.simulations if g.get_card_set(set).has_card(card)]
        self.populate_simulations()

    def epoch(self):
        self.simulations = [g for g in self.simulations if g.epoch() and g.like(self.game)]
        if self.game.verbose: print('%d/%d simulations dropped' % (self.n_simulations - len(self.simulations), self.n_simulations))
        self.populate_simulations()

    def score_game(self, game):
        score = 0
        score -= sum(10 for c in self.cards if c.dead)
        score += 3 * len(self._possible_actions(game))
        if game.alive_players:
            score += sum(10 for p in game.alive_players if p != self for c in p.cards if c.dead) / len(game.alive_players)
        if game.winner is not None and game.winner.nickname == self.nickname:
            score += 100
        return score

    def act(self):
        from coup.game import SimulatedGame
        actions = self._possible_actions()
        simulations = ((random.choice(actions), SimulatedGame(random.choice(self.simulations), self)) for _ in range(self.n_simulations))
        simulations = ((action, game.epoch(action)) for action, game in simulations if action.can(game))
        simulations = ((action, game.epochs(self.n_epochs)) for action, game in simulations)
        best_action = max(simulations, key=lambda x: self.score_game(x[1]))[0]
        return best_action


class AntiSmartPlayer(SmartPlayer):
    def score_game(self, game):
        return - super().score_game(game)


PLAYER_TYPE = dict(
    dumb=DumbPlayer,
    true=TruePlayer,
    smart=SmartPlayer,
)

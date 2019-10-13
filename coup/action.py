from coup.card import *


class Action:
    __card_category__ = None
    __cost__ = 0

    def __init__(self, player):
        self.player = player.nickname
        self.game = player.game

    def can(self, game=None):
        player = (self.game if game is None else game).get_player(self.player)
        return self.__cost__ < player.treasure < 10 + self.__cost__

    def truly_can(self, game=None):
        player = (self.game if game is None else game).get_player(self.player)
        return self.__card_category__ is None or player.has_card(self.__card_category__)

    def do(self, game=None):
        raise NotImplementedError


class SimpleAction(Action):
    pass


class DirectAction(Action):

    def __init__(self, player, other):
        super().__init__(player)
        self.other = other.nickname


class BlockAction(Action):
    __blocked_action__ = None

    def __init__(self, player, other, action):
        super().__init__(player)
        self.other = other.nickname
        self.action = action

    def can(self, game=None):
        if not isinstance(self.action, self.__blocked_action__):
            return False
        if isinstance(self.action, SimpleAction):
            return True
        elif isinstance(self.action, DirectAction):
            return (self.player, self.other) == (self.action.other, self.action.player)
        else:
            raise TypeError(self.action)

    def do(self, game=None):
        pass

    def __str__(self):
        return '%s blocks %s with %s' % (self.player, self.other, self.__card_category__.__nickname__)


class BankAction(SimpleAction):
    def do(self, game=None):
        (self.game if game is None else game).get_player(self.player).income(1)

    def can(self, game=None):
        return (self.game if game is None else game).get_player(self.player).treasure < 10

    def __str__(self):
        return '%s takes 1 coin' % self.player


class ForeignAction(SimpleAction):
    def do(self, game=None):
        (self.game if game is None else game).get_player(self.player).income(2)

    def can(self, game=None):
        return (self.game if game is None else game).get_player(self.player).treasure < 10

    def __str__(self):
        return '%s takes 2 coins' % self.player


class DuchessBlockForeignAction(BlockAction):
    __blocked_action__ = ForeignAction
    __card_category__ = DuchessCard


class KillAction(DirectAction):
    __cost__ = 7

    def do(self, game=None):
        game = self.game if game is None else game
        game.kill(game.get_player(self.other))

    def __str__(self):
        return '%s kills %s' % (self.player, self.other)


class DuchessAction(SimpleAction):
    __card_category__ = DuchessCard

    def do(self, game=None):
        (self.game if game is None else game).get_player(self.player).income(3)

    def can(self, game=None):
        return (self.game if game is None else game).get_player(self.player).treasure < 10

    def __str__(self):
        return '%s takes 3 coins' % self.player


class CaptainAction(DirectAction):
    __card_category__ = CaptainCard

    def do(self, game=None):
        n = min((self.game if game is None else game).get_player(self.other).treasure, 2)
        (self.game if game is None else game).get_player(self.other).pay(n)
        (self.game if game is None else game).get_player(self.player).income(n)

    def can(self, game=None):
        return (self.game if game is None else game).get_player(self.player).treasure < 10

    def __str__(self):
        return '%s steals 2 coins from %s' % (self.player, self.other)


class CaptainBlockCaptainAction(BlockAction):
    __card_category__ = CaptainCard
    __blocked_action__ = CaptainAction


class InquisitorBlockCaptainAction(BlockAction):
    __card_category__ = InquisitorCard
    __blocked_action__ = CaptainAction


class MurdererAction(DirectAction):
    __cost__ = 3

    def do(self, game=None):
        game = self.game if game is None else game
        game.kill(game.get_player(self.other))

    def __str__(self):
        return '%s murders %s' % (self.player, self.other)


class CountessBlockMurdererAction(BlockAction):
    __blocked_action__ = MurdererAction
    __card_category__ = CountessCard


class InquisitorMiddleAction(SimpleAction):
    __card_category__ = InquisitorCard

    def do(self, game=None):
        player = (self.game if game is None else game).get_player(self.player)
        player.game.middle.shuffle()
        player.learn_card(player.game.middle.cards[0], player.game.middle)

    def __str__(self):
        return '%s looks at the middle' % self.player


class InquisitorPlayerAction(DirectAction):
    __card_category__ = InquisitorCard

    def do(self, game=None):
        player = (self.game if game is None else game).get_player(self.player)
        other = (self.game if game is None else game).get_player(self.other)
        player.learn_card(other.choose_look(), other)

    def __str__(self):
        return '%s looks at %s' % (self.player, self.other)


ACTIONS = [
    BankAction, ForeignAction, KillAction,
    DuchessAction, DuchessBlockForeignAction,
    CaptainAction, CaptainBlockCaptainAction, InquisitorBlockCaptainAction,
    MurdererAction, CountessBlockMurdererAction,
    InquisitorMiddleAction, InquisitorPlayerAction,
]

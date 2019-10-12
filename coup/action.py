from coup.card import *


class Action:
    __card_category__ = None
    __cost__ = 0

    def __init__(self, player, other=None):
        self.player = player
        self.other = other
        self.blocked = False

    def can(self):
        return self.player.treasure < 10 + self.__cost__ and self.player.treasure >= self.__cost__

    def truly_can(self):
        return self.__card_category__ is None or self.player.has_card(self.__card_category__)

    def do(self, game):
        raise NotImplementedError


class SimpleAction(Action):
    pass


class DirectAction(SimpleAction):
    pass


class BlockAction(Action):
    __blocked_action__ = None

    def __init__(self, player, action, other):
        super().__init__(player, )
        self.other = other
        self.action = action

    def can(self):
        return isinstance(self.action, self.__blocked_action__)

    def do(self, game):
        pass

    def __str__(self):
        return '%s blocks %s with %s' % (self.player, self.other, self.__card_category__.__nickname__)


class BankAction(SimpleAction):
    def do(self, game):
        self.player.income(1)

    def can(self):
        return self.player.treasure < 10

    def __str__(self):
        return '%s takes 1 coin' % self.player


class ForeignAction(SimpleAction):
    def do(self, game):
        self.player.income(2)

    def can(self):
        return self.player.treasure < 10

    def __str__(self):
        return '%s takes 2 coins' % self.player


class DuchessBlockForeignAction(BlockAction):
    __blocked_action__ = ForeignAction
    __card_category__ = DuchessCard


class KillAction(DirectAction):
    __cost__ = 7

    def do(self, game):
        game.kill(self.other)

    def __str__(self):
        return '%s kills %s' % (self.player, self.other)


class DuchessAction(SimpleAction):
    __card_category__ = DuchessCard

    def do(self, game):
        self.player.income(3)

    def can(self):
        return self.player.treasure < 10

    def __str__(self):
        return '%s takes 3 coins' % self.player


class CaptainAction(DirectAction):
    __card_category__ = CaptainCard

    def do(self, game):
        n = min(self.other.treasure, 2)
        self.other.pay(n)
        self.player.income(n)

    def can(self):
        return self.player.treasure < 10

    def __str__(self):
        n = min(self.other.treasure, 2)
        return '%s steals %d coins from %s' % (self.player, n, self.other)


class CaptainBlockCaptainAction(BlockAction):
    __card_category__ = CaptainCard
    __blocked_action__ = CaptainAction


class InquisitorBlockCaptainAction(BlockAction):
    __card_category__ = InquisitorCard
    __blocked_action__ = CaptainAction


class MurdererAction(DirectAction):
    __cost__ = 3

    def do(self, game):
        game.kill(self.other)

    def __str__(self):
        return '%s murders %s' % (self.player, self.other)


class LadyBlockMurdererAction(BlockAction):
    __blocked_action__ = MurdererAction
    __card_category__ = LadyCard


class InquisitorMiddleAction(SimpleAction):
    __card_category__ = InquisitorCard

    def do(self, game):
        game.middle.shuffle()
        self.player.learn_card(game.middle._cards[0], game.middle)

    def __str__(self):
        return '%s looks at the middle' % self.player


class InquisitorPlayerAction(DirectAction):
    __card_category__ = InquisitorCard

    def do(self, game):
        self.player.learn_card(self.other.choose_look(), self.other)

    def __str__(self):
        return '%s looks at %s' % (self.player, self.other)


ACTIONS = [
    BankAction, ForeignAction, KillAction,
    DuchessAction, DuchessBlockForeignAction,
    CaptainAction, CaptainBlockCaptainAction, InquisitorBlockCaptainAction,
    MurdererAction, LadyBlockMurdererAction,
    InquisitorMiddleAction, InquisitorPlayerAction,
]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import unittest

from ..game import Game
from ..player import Player
from ..card import *


class Test(unittest.TestCase):

    game = None

    def setUp(self):
        self.game = Game(None)

    def test_insert(self):
        p0 = Player(self.game, "Player 0")
        p1 = Player(self.game, "Player 1")
        p2 = Player(self.game, "Player 2")

        self.assertEqual(p0, p2.next)
        self.assertEqual(p1, p0.next)
        self.assertEqual(p2, p1.next)

        self.assertEqual(p0.prev, p2)
        self.assertEqual(p1.prev, p0)
        self.assertEqual(p2.prev, p1)

    def test_reverse(self):
        p0 = Player(self.game, "Player 0")
        p1 = Player(self.game, "Player 1")
        p2 = Player(self.game, "Player 2")
        self.game.reverse()
        p3 = Player(self.game, "Player 3")

        self.assertEqual(p0, p3.next)
        self.assertEqual(p1, p2.next)
        self.assertEqual(p2, p0.next)
        self.assertEqual(p3, p1.next)

        self.assertEqual(p0, p2.prev)
        self.assertEqual(p1, p3.prev)
        self.assertEqual(p2, p1.prev)
        self.assertEqual(p3, p0.prev)

    def test_leave(self):
        p0 = Player(self.game, "Player 0")
        p1 = Player(self.game, "Player 1")
        p2 = Player(self.game, "Player 2")

        p1.leave()

        self.assertEqual(p0, p2.next)
        self.assertEqual(p2, p0.next)

    def test_draw(self):
        p = Player(self.game, "Player 0")

        deck_before = len(self.game.deck.cards)
        top_card = self.game.deck.cards[-1]

        p.draw()

        self.assertEqual(top_card, p.cards[-1])
        self.assertEqual(deck_before, len(self.game.deck.cards) + 1)

    def test_draw_two(self):
        p = Player(self.game, "Player 0")

        deck_before = len(self.game.deck.cards)
        self.game.draw_counter = 2

        p.draw()

        self.assertEqual(deck_before, len(self.game.deck.cards) + 2)

    def test_playable_cards_simple(self):
        p = Player(self.game, "Player 0")

        self.game.last_card = Card(RED, '5')

        p.cards = [Card(RED, '0'), Card(RED, '5'), Card(BLUE, '0'),
                   Card(GREEN, '5'), Card(GREEN, '8')]

        expected = [Card(RED, '0'), Card(RED, '5'),
                    Card(GREEN, '5')]

        self.assertListEqual(p.playable_cards(), expected)

    def test_playable_cards_on_draw_two(self):
        p = Player(self.game, "Player 0")

        self.game.last_card = Card(RED, DRAW_TWO)
        self.game.draw_counter = 2

        p.cards = [Card(RED, DRAW_TWO), Card(RED, '5'),
                   Card(BLUE, '0'), Card(GREEN, '5'),
                   Card(GREEN, DRAW_TWO)]

        expected = [Card(RED, DRAW_TWO), Card(GREEN, DRAW_TWO)]

        self.assertListEqual(p.playable_cards(), expected)

    def test_playable_cards_on_draw_four(self):
        p = Player(self.game, "Player 0")

        self.game.last_card = Card(RED, None, DRAW_FOUR)
        self.game.draw_counter = 4

        p.cards = [Card(RED, DRAW_TWO), Card(RED, '5'),
                   Card(BLUE, '0'), Card(GREEN, '5'),
                   Card(GREEN, DRAW_TWO),
                   Card(None, None, DRAW_FOUR),
                   Card(None, None, CHOOSE)]

        expected = list()

        self.assertListEqual(p.playable_cards(), expected)

    def test_bluffing(self):
        p = Player(self.game, "Player 0")
        Player(self.game, "Player 01")

        self.game.last_card = Card(RED, '1')

        p.cards = [Card(RED, DRAW_TWO), Card(RED, '5'),
                   Card(BLUE, '0'), Card(GREEN, '5'),
                   Card(RED, '5'), Card(GREEN, DRAW_TWO),
                   Card(None, None, DRAW_FOUR),
                   Card(None, None, CHOOSE)]

        p.playable_cards()
        self.assertTrue(p.bluffing)

        p.cards = [Card(BLUE, '1'), Card(GREEN, '1'),
                   Card(GREEN, DRAW_TWO),
                   Card(None, None, DRAW_FOUR),
                   Card(None, None, CHOOSE)]

        p.playable_cards()

        p.play(Card(None, None, DRAW_FOUR))
        self.game.choose_color(GREEN)

        self.assertFalse(self.game.current_player.prev.bluffing)

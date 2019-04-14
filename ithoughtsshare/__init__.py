# pylint: disable=missing-docstring
from ithoughtsshare.ithoughts_notes import StateDispatcher


def run():
    dispatcher = StateDispatcher()
    dispatcher.next_state('FORWARD')

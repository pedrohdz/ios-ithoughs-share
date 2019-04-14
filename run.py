#!/usr/bin/env python
# pylint: disable=missing-docstring

import logging as log
import ithoughtsshare


if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)
    ithoughtsshare.run()

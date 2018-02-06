# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def is_urlopen_error(exception):
    return '<urlopen error [Errno -2] Name or service not known>' in str(exception) or \
           '<urlopen error [Errno 8] nodename nor servname provided, or not known' in str(exception) or \
           '<urlopen error [Errno -5] No address associated with hostname>' in str(exception) or \
           '<urlopen error [Errno -3] Temporary failure in name resolution>' in str(exception)

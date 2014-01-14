#
# linter.py
# Linter for SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Aparajita Fishman
# Copyright (c) 2013 Aparajita Fishman
#
# License: MIT
#

"""This module exports the JSHint plugin linter class."""

from SublimeLinter.lint import Linter
import re


class JSHint(Linter):

    """Provides an interface to the jshint executable."""

    syntax = ('javascript', 'html')
    cmd = 'jshint --verbose * -'
    regex = (
        r'^(?:(?P<fail>ERROR: .+)|'
        r'.+?: line (?P<line>\d+), col (?P<col>\d+), '
        r'(?P<message>'
        r'\'(?P<undef>.+)\'.+(?=.+W098)' #undefined warnings
        r'|.+\'(?P<actual>.+)\'\.(?=.+W116)' #non strict operators
        r'|.+\'(?P<unexpected>.+)\'\.(?=.+W016)' #unexpected use of ++ etc
        r'|.+)' #match all messages
        r' \((?:(?P<error>E)|(?P<warning>W))(?P<code>\d+)\))' #capture error, warning and code
    )
    selectors = {
        'html': 'source.js.embedded.html'
    }
    config_file = ('--config', '.jshintrc', '~')

    def split_match(self, match):
        """
        Return the components of the match.

        We override this to catch linter error messages and place them
        at the top of the file.

        """

        #restore word regex to default each iteration
        self.word_re = None

        if match:
            fail = match.group('fail')
            hasError = match.group('error')
            hasWarning = match.group('warning')
            message = match.group('message')
            code = match.group('code')
            line = int(match.group('line')) -1
            col = int(match.group('col')) -1
            near = None


            if fail:
                # match, line, col, error, warning, message, near
                return match, 0, 0, True, False, fail, None
            #mark the undefined word
            elif code == '098':
                col = col - len(match.group('undef'))
            #if we have a operator == or != manually change the column, near won't work here as we might have multiple ==/!= on a line
            elif code == '116':
                self.word_re = re.compile(match.group('actual'));
                col = col - len(match.group('actual'))
            #now jshint place the column in front, and as such we need to change our word matching regex, and keep the column info
            elif code == '016':
                self.word_re = re.compile('[+-]+');

            return match, line, col, hasError, hasWarning, message, near


        return super().split_match(match)

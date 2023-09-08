import sys

from frida_tools.application import ConsoleApplication
from xpcspy.lib.types import Filter

from agent import Agent


class XPCSpyApplication(ConsoleApplication):
    def _usage(self):
        return "%(prog)s"

    def _needs_target(self):
        return True

    def _initialize(self, parser, options, args):
        self._filter = Filter.from_str("o:*")
        self._should_parse = True
        self._print_timestamp = False
        self._target = ("name", "AppleSpell")

    def _start(self):
        agent = Agent(
            self._filter,
            self._should_parse,
            self._session,
            self._reactor,
            self._print_timestamp,
        )
        agent.start_hooking(self)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.append("AppleSpell")

    app = XPCSpyApplication()
    app.run()

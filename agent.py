from os import path
from collections import OrderedDict

import xpcspy
from xpcspy.lib.types import Event
import subprocess
import json
import traceback


def convert_value(value):
    if value["type"] == "ascii_string":
        return value["value"]
    elif value["type"] == "unicode_string":
        return value["value"]
    elif value["type"] == "int":
        return value["value"]
    elif value["type"] == "uid":
        return value["value"]
    elif value["type"] == "dict":
        return convert_dict(value["entries"])
    elif value["type"] == "array":
        return convert_array(value["entries"])
    else:
        return json.dumps(value)


def convert_dict(obj):
    return {entry["key"]["value"]: convert_value(entry["value"]) for entry in obj}


def convert_array(obj):
    return [convert_value(val) for val in obj]


class Agent:
    def __init__(self, filter, should_parse, session, reactor, print_timestamp=False):
        """
        Initialize the Frida agent
        """
        self._pending_events = (
            OrderedDict()
        )  # A map of stacks, each stack holding events for that particular timestamp
        self._filter = filter
        self._should_parse = should_parse
        self._print_timestamp = print_timestamp
        self._script_path = path.join(path.dirname(xpcspy.__file__), "..", "_agent.js")
        with open(self._script_path) as src_f:
            script_src = src_f.read()
        self._script = session.create_script(script_src)
        self._reactor = reactor
        self._agent = None

    def start_hooking(self, ui):
        def on_message(message, data):
            self._reactor.schedule(lambda: self._on_message(message, data, ui))

        self._script.on("message", on_message)
        self._script.load()
        ui._update_status("Installing hooks...")
        self._agent = self._script.exports
        self._agent.install_hooks(self._filter, self._should_parse)

    def _on_message(self, message, data, ui):
        mtype = message["payload"]["type"]

        if mtype == "agent:hooks_installed":
            ui._update_status("Hooks installed, intercepting messages...")
            ui._resume()
        elif mtype == "agent:trace:symbol":
            symbol = message["payload"]["message"]["symbol"]
            timestamp = message["payload"]["message"]["timestamp"]
            if timestamp in self._pending_events:
                self._pending_events[timestamp].append(Event(symbol))
            else:
                self._pending_events.update({timestamp: [Event(symbol)]})
        elif mtype == "agent:trace:data":
            timestamp = message["payload"]["message"]["timestamp"]
            data = message["payload"]["message"]["data"]
            self._pending_events[timestamp][-1].data = data
        else:
            ui._print(f"Unhandled message {message}")

        self.flush_pending_events(ui)

    def flush_pending_events(self, ui):
        """Flush pending events that are ready, i.e. have received both its symbol and data"""
        for ts, events_stack in list(self._pending_events.items()):
            while len(events_stack) > 0:
                last_event = events_stack[-1]  # Peek

                if last_event.data == None:
                    return

                for line in last_event.data["message"].splitlines():
                    if "<62706c69" in line:
                        encoded_bplist = line[
                            line.index("<") + 1 : line.index(">", -1)
                        ].replace(" ", "")
                        cmd = f"echo {encoded_bplist} | xxd -r -p | fq d -V"
                        decoded_bplist = subprocess.check_output(
                            cmd, shell=True
                        ).decode("utf-8")
                        payload = json.loads(decoded_bplist)

                        print(payload)

                        data = convert_array(
                            payload["objects"]["entries"][3]["value"]["entries"]
                        )
                        indices = data[1]

                        if len(indices["NS.objects"]) == 0:
                            continue
                        else:
                            indices = indices["NS.objects"]

                        print("-" * 40)
                        lines_printed = 0

                        for i in indices:
                            try:
                                if data[i]["$class"] in [4, 10, 12]:
                                    replacement_str = data[
                                        data[i]["NSReplacementString"]
                                    ]
                                    promoted = "NSIsPromoted" in data[i]

                                    if promoted:
                                        print(f"*** {replacement_str} ***")
                                    else:
                                        print(replacement_str)
                                elif data[i]["$class"] == 6:
                                    replacement_str = data[
                                        data[i]["NSReplacementString"]
                                    ]
                                    print(f"*** {replacement_str} ***")
                                else:
                                    continue

                                lines_printed += 1
                            except:
                                print(traceback.format_exc())
                                print(data)

                events_stack.pop()
            del self._pending_events[ts]

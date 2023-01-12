from espytrace import sysview
from espytrace import apptrace

import traceback
import os

class SysViewReader:
    def __init__(self):
        self.parsers: list[sysview.SysViewMultiTraceDataParser] = []

    def add_file(self, filename, sysview_mapfile):
        print("Reading", filename)
        parser = sysview.SysViewMultiTraceDataParser(
            print_events=False, core_id=len(self.parsers))
        self.parsers.append(parser)

        try:
            sysview.parse_trace(apptrace.reader_create('file://%s' % filename, 0),
                                parser, os.path.join(os.path.dirname(__file__), sysview_mapfile))
        except Exception as e:
            if not str(e).startswith("Timeout"):
                traceback.print_exc()
        print("Read", len(parser.events), "events")

    def get_events(self):
        events = []
        for parser in self.parsers:
            events.extend(parser.events)
        return events

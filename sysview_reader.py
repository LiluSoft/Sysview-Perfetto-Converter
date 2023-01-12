
from espytrace import sysview
from espytrace import apptrace

import traceback
import os
# import json
# from scoping import scoping
# from google.protobuf.json_format import MessageToDict

# parsers = []

# cores_num = 2

# for i in range(cores_num):
#     # create parser
#     try:
#         parser = sysview.SysViewMultiTraceDataParser(print_events=False, core_id=i)
#         # parser.add_stream_parser(sysview.SysViewTraceDataParser.STREAMID_HEAP,
#         #                             sysview.SysViewHeapTraceDataParser(print_events=False, core_id=i))
#         # parser.add_stream_parser(sysview.SysViewTraceDataParser.STREAMID_LOG,
#         #                             sysview.SysViewLogTraceDataParser(print_events=False, core_id=i))
#         parsers.append(parser)
#     except Exception as e:
#             traceback.print_exc()

# app_filename = "app-cpu2.SVDat"
# pro_filename = "pro-cpu2.SVDat"

# try:
#     sysview.parse_trace(apptrace.reader_create( 'file://%s' % app_filename,0), parsers[0], os.path.join(os.path.dirname(__file__), 'SYSVIEW_FreeRTOS.txt'))   
# except Exception as e:
#     print("err",e)
#     pass

# try:
#     sysview.parse_trace(apptrace.reader_create( 'file://%s' % pro_filename, 0), parsers[1], os.path.join(os.path.dirname(__file__), 'SYSVIEW_FreeRTOS.txt'))
# except Exception as e:
#     print("err",e)
#     pass

# data = []

# last_event = None
# skip_count = 0

# def normalize_event(evt, params):
#     return {
#         'id':evt.id, 
#         'ts':evt.ts, 
#         'core_id':evt.core_id, 
#         'name':evt.name, 
#         'plen':evt.plen,
#         'params':params
#     }



# def is_same_evt(evt1, evt2):
#     # print("evt1", evt1, "evt2", evt2)
#     if (evt1 == None or evt2 == None):
#         return False
#     if evt1["name"] == evt2["name"] and evt1["core_id"] == evt2["core_id"] and evt1["params"] == evt2["params"]:
#         return True
#     return False

# for i in range(cores_num):
#     for evt in parsers[i].events:
#         params = {}
#         for p in evt.params:
#             params[p] = evt.params[p].value
        
#         normalized_event = normalize_event(evt, params)

#         if is_same_evt(last_event, normalized_event):
#             # nop
#             skip_count = skip_count + 1
#         else:
#             if skip_count > 0:
#                 print("skipping", skip_count)
#                 last_event_end = last_event
#                 if (last_event_end != None):
#                     last_event_end["name"] = last_event_end["name"] + "End"
#                     data.append(last_event_end)
#             data.append(normalized_event)
#             skip_count = 0
#         last_event = normalized_event

# with open('trace.json', 'w') as outfile:
#     json.dump(data, outfile)



class SysViewReader:
    def __init__(self):
        self.parsers:list[sysview.SysViewMultiTraceDataParser] = []

    def add_file(self, filename, sysview_mapfile):
        print("Reading", filename)
        parser = sysview.SysViewMultiTraceDataParser(print_events=False, core_id=len(self.parsers))
        self.parsers.append(parser)
        
        try:
            sysview.parse_trace(apptrace.reader_create( 'file://%s' % filename,0), parser, os.path.join(os.path.dirname(__file__), sysview_mapfile))
        except Exception as e:
            if not str(e).startswith("Timeout"):
                traceback.print_exc()
        print("Read", len(parser.events), "events")

    def get_events(self):
        events = []
        for parser in self.parsers:
            events.extend(parser.events)
        return events
    

import argparse

from sysview_reader import SysViewReader
import sysview_event_processor
import perfetto_writer

# import espytrace.apptrace as apptrace
# import espytrace.sysview as sysview
# import traceback
# import os
import json
# import perfetto_trace.perfetto_trace_pb2
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

# #help(parsers[0].events)

# # for evt in parsers[0].events:
# #      print(evt.id, evt.ts, evt.core_id, evt.name, evt.plen)
# #      for p in evt.params:
# #          print(p,evt.params[p].value)
# #print(parsers[0].events,parsers[1].events )


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


# trace = perfetto_trace.perfetto_trace_pb2.Trace()

# with scoping():
#     packet = trace.packet.add()
#     data_sources = packet.trace_config.data_sources.add()
#     data_sources.config.name = "linux.process_stats"
#     # data_sources.config.ftrace_config.ftrace_events.append("event1")

# system_info_packet = trace.packet.add()
# system_info_packet.system_info.utsname.sysname = "Linux"

# def add_task_info(ts, pid, ppid, name):
#     with scoping():
#             packet = trace.packet.add()
#             packet.timestamp = ts
#             with scoping():
#                 process = packet.process_tree.processes.add()
#                 process.pid = pid
#                 process.ppid = ppid
#                 process.cmdline.append(name)
# add_task_info(0, 1,0,"Init" )
# # add_task_info(0, 2, 0, "rtos")

# def add_cpu_idle(packet, ts, core_id):
#     event = packet.ftrace_events.event.add()
#     event.timestamp = ts
#     event.pid = 0
#     event.cpu_idle.cpu_id = core_id
#     event.cpu_idle.state = 0
# def add_cpu_wakeup(packet, ts, core_id):
#     event = packet.ftrace_events.event.add()
#     event.timestamp = ts
#     event.pid = 0
#     event.cpu_idle.cpu_id = core_id
#     event.cpu_idle.state = 4294967295

# cpus = {}


# def get_cpu(cpuid):
#     if cpuid in cpus:
#         return cpus[cpuid]
#     packet = trace.packet.add()
#     packet.ftrace_events.cpu = cpuid
#     cpus[cpuid] = packet
#     return cpus[cpuid]

# cpus_last_pid = {}

# def get_cpu_last_pid(cpuid):
#     if cpuid in cpus_last_pid:
#         return cpus_last_pid[cpuid]
#     return 0

# def set_cpu_last_pid(cpuid, last_pid):
#     cpus_last_pid[cpuid] = last_pid

# for sample in data:
#     if sample["name"] == "svInit":
#         with scoping():
#             packet = trace.packet.add()
#             packet.ftrace_events.cpu = sample["core_id"]
#             add_cpu_wakeup(packet,int(sample["ts"] * 1000000000), sample["core_id"] )
#             # with scoping():
#             #     event = packet.ftrace_events.event.add()
#             #     event.timestamp = int(sample["ts"] * 1000000000)
#             #     event.pid = 0
#             #     event.cpu_idle.state = 0
#             #     event.cpu_idle.cpu_id =sample["core_id"]
#             with scoping():
#                 event = packet.ftrace_events.event.add()
#                 event.timestamp = int(sample["ts"] * 1000000000)
#                 event.pid = 0
#                 event.cpu_frequency.state = int(sample["params"]["cpu_freq"] / 1000)
#                 event.cpu_frequency.cpu_id = sample["core_id"]
#     elif sample["name"] == "svSysDesc":
#         desc = sample["params"]["desc"]
#         descitems = desc.split(",")
#         for item in descitems:
#             itemparts = item.split("=")
#             if itemparts[0] == "N": # application name
#                 system_info_packet.system_info.utsname.version = itemparts[1]
#             elif itemparts[0] == "D": # device
#                 system_info_packet.system_info.utsname.machine = itemparts[1]
#             elif itemparts[0].startswith("I"): # interrupt information
#                 packet = get_cpu(sample["core_id"])
#                 with scoping():
#                     event = packet.ftrace_events.event.add()
#                     event.timestamp = int(sample["ts"] * 1000000000)
#                     event.pid = 1
#                     event.print.buf = "I|" + str(sample["core_id"]) + "|" + desc
#                 interrupt_name = str(sample["core_id"]) + "/" + itemparts[0][1:] + "/" + itemparts[1]
#                 interrupt_number = (sample["core_id"] * 100) + int(itemparts[0][2:])

#                 add_task_info(int(sample["ts"] * 1000000000),interrupt_number, 0, interrupt_name)
#     elif sample["name"] == "svTaskInfo":
#         add_task_info(int(sample["ts"] * 1000000000),sample["params"]["tid"], sample["params"]["tid"], sample["params"]["name"])
#     elif sample["name"] == "svStackInfo":
#         packet = get_cpu(sample["core_id"])
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = sample["params"]["tid"]
#             event.print.buf = "I|" + str(sample["params"]["tid"]) + "|" + "Stack " + str(sample["params"]["sz"]) + " bytes"
#     elif sample["name"] == "svTaskStartExec":
#         packet = get_cpu(sample["core_id"])
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = sample["params"]["tid"]
#             event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
#             if event.sched_switch.prev_pid == 0:
#                 event.sched_switch.prev_comm = "swapper"
#             event.sched_switch.next_pid = sample["params"]["tid"]
#             set_cpu_last_pid(sample["core_id"], event.pid)
#             # add_cpu_wakeup(packet,event.timestamp, sample["core_id"] )
#     elif sample["name"] == "svIsrEnter":
#         packet = get_cpu(sample["core_id"])
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = get_cpu_last_pid(sample["core_id"])
#             event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
#             if event.sched_switch.prev_pid == 0:
#                 event.sched_switch.prev_comm = "swapper"
#             event.sched_switch.next_pid = (sample["core_id"] * 100) + sample["params"]["irq_num"]
#             event.sched_switch.next_comm = "I#" + str(sample["params"]["irq_num"])
#             set_cpu_last_pid(sample["core_id"], event.sched_switch.next_pid)
#             # add_cpu_wakeup(packet,event.timestamp, sample["core_id"] )
#     elif sample["name"] == "svExitIsrToScheduler":
#         packet = get_cpu(sample["core_id"])
       
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = get_cpu_last_pid(sample["core_id"])
#             event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
#             if event.sched_switch.prev_pid == 0:
#                 event.sched_switch.prev_comm = "swapper"
#             event.sched_switch.next_comm = "swapper"
#             event.sched_switch.next_pid = 0
#             # add_cpu_idle(packet,event.timestamp, sample["core_id"] )
#         # with scoping():
#         #     event = packet.ftrace_events.event.add()
#         #     event.timestamp = int(sample["ts"] * 1000000000)
#         #     event.pid = get_cpu_last_pid(sample["core_id"])
#         #     event.sched_process_wait.pid = get_cpu_last_pid(sample["core_id"])
#         #     add_cpu_idle(packet,event.timestamp, sample["core_id"] )

#             # event = packet.ftrace_events.event.add()
#             # event.timestamp = int(sample["ts"] * 1000000000)
#             # event.pid = get_cpu_last_pid(sample["core_id"])
#             # event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
#             # event.sched_switch.next_comm = "Scheduler"
#             # event.sched_switch.next_pid = 0
#             # set_cpu_last_pid(sample["core_id"], 0)
#     # elif sample["name"] == "svTaskStartReady":
#     #     packet = get_cpu(sample["core_id"])
#     #     with scoping():
#     #         event = packet.ftrace_events.event.add()
#     #         event.timestamp = int(sample["ts"] * 1000000000)
#     #         event.pid = sample["params"]["tid"]
#     #         event.sched_wakeup.pid = sample["params"]["tid"]
#     #         event.sched_wakeup.target_cpu = sample["core_id"]
#     elif sample["name"] == "svTaskStopReady":
#         packet = get_cpu(sample["core_id"])
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = sample["params"]["tid"]
#             event.sched_wakeup.pid = sample["params"]["tid"]
#             event.sched_wakeup.target_cpu = sample["core_id"]
#     elif sample["name"] == "vTaskDelay":
#         packet = get_cpu(sample["core_id"])
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = get_cpu_last_pid(sample["core_id"])
#             event.sched_process_wait.pid = get_cpu_last_pid(sample["core_id"])
#     elif sample["name"] == "vTaskDelete":
#         packet = get_cpu(sample["core_id"])
#         with scoping():
#             event = packet.ftrace_events.event.add()
#             event.timestamp = int(sample["ts"] * 1000000000)
#             event.pid = sample["params"]["xTaskToDelete"]
#             event.sched_process_exit.pid = sample["params"]["xTaskToDelete"]
#     elif sample["name"] == "svIdle":
#         packet = get_cpu(sample["core_id"])
#         add_cpu_idle(packet,int(sample["ts"] * 1000000000),sample["core_id"] )

# with open("trace_perfetto.json", "w") as perfetto_trace_file:
#     json.dump(MessageToDict(trace), perfetto_trace_file)

# with open('cpu1_trace', 'wb') as f:
#     f.write(perfetto_trace.perfetto_trace_pb2.Trace.SerializeToString(trace))



parser = argparse.ArgumentParser(
                    prog = 'tracer',
                    description = 'Convert Segger SystemView to Perfetto ftrace format'
                    )

# parser.add_argument('filename')           # positional argument
parser.add_argument("-i", dest="input_filename", action="extend", nargs="+", type=str, help='add input sysview file (svdat)')
parser.add_argument('--dump_input', dest="dump_input",type=str, help='dumps the parsed input to json file')
parser.add_argument("-p", dest="ftrace_output", help='ftrace output file name')
parser.add_argument('--dump_ftrace_json', dest="dump_ftrace_json",type=str,help='dumps the generated ftrace as json')
parser.add_argument('--sysview_mapfile', dest="sysview_mapfile", type=str, help="SystemView Map File", default="SYSVIEW_FreeRTOS.txt")


args = vars(parser.parse_args())
# print(args)
print(parser.prog,"-", parser.description)

sysview_reader = SysViewReader()
processed_events = []

for filename in args["input_filename"]:
    sysview_reader.add_file(filename,args["sysview_mapfile"])

processed_events = sysview_event_processor.process(sysview_reader.get_events())

if args["dump_input"]:
    with open(args["dump_input"], 'w') as outfile:
        json.dump(processed_events, outfile)

ftrace = perfetto_writer.convert(processed_events)

if args["dump_ftrace_json"]:
    print('Writing ftrace json dump', args["dump_ftrace_json"])
    with open(args["dump_ftrace_json"], "w") as perfetto_trace_file:
        perfetto_trace_file.write(perfetto_writer.trace_to_json(ftrace))

if args["ftrace_output"]:
    print('Writing ftrace', args["ftrace_output"])
    with open(args["ftrace_output"], 'wb') as f:
        f.write(perfetto_writer.serialize_trace(ftrace))

print('Done')


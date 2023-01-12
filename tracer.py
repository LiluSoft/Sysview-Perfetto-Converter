import argparse

from sysview_reader import SysViewReader
import sysview_event_processor
import perfetto_writer
import json

parser = argparse.ArgumentParser(
    prog='tracer',
    description='Convert Segger SystemView to Perfetto ftrace format'
)

parser.add_argument("-i", dest="input_filename", action="extend",
                    nargs="+", type=str, help='add input sysview file (svdat)')
parser.add_argument('--dump_input', dest="dump_input",
                    type=str, help='dumps the parsed input to json file')
parser.add_argument("-p", dest="ftrace_output", help='ftrace output file name')
parser.add_argument('--dump_ftrace_json', dest="dump_ftrace_json",
                    type=str, help='dumps the generated ftrace as json')
parser.add_argument('--sysview_mapfile', dest="sysview_mapfile",
                    type=str, help="SystemView Map File", default="SYSVIEW_FreeRTOS.txt")


args = vars(parser.parse_args())
# print(args)
print(parser.prog, "-", parser.description)

sysview_reader = SysViewReader()
processed_events = []

for filename in args["input_filename"]:
    sysview_reader.add_file(filename, args["sysview_mapfile"])

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

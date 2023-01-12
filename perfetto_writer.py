from scoping import scoping
import perfetto.perfetto_trace_pb2
from google.protobuf.json_format import MessageToDict
import json

def convert(events):

    trace = perfetto.perfetto_trace_pb2.Trace()

    with scoping():
        packet = trace.packet.add()
        data_sources = packet.trace_config.data_sources.add()
        data_sources.config.name = "linux.process_stats"
        # data_sources.config.ftrace_config.ftrace_events.append("event1")

    system_info_packet = trace.packet.add()
    system_info_packet.system_info.utsname.sysname = "Linux"

    def add_task_info(ts, pid, ppid, name):
        with scoping():
                packet = trace.packet.add()
                packet.timestamp = ts
                with scoping():
                    process = packet.process_tree.processes.add()
                    process.pid = pid
                    process.ppid = ppid
                    process.cmdline.append(name)
    add_task_info(0, 1,0,"Init" )
    # add_task_info(0, 2, 0, "rtos")

    def add_cpu_idle(packet, ts, core_id):
        event = packet.ftrace_events.event.add()
        event.timestamp = ts
        event.pid = 0
        event.cpu_idle.cpu_id = core_id
        event.cpu_idle.state = 0
    def add_cpu_wakeup(packet, ts, core_id):
        event = packet.ftrace_events.event.add()
        event.timestamp = ts
        event.pid = 0
        event.cpu_idle.cpu_id = core_id
        event.cpu_idle.state = 4294967295

    cpus = {}


    def get_cpu(cpuid):
        if cpuid in cpus:
            return cpus[cpuid]
        packet = trace.packet.add()
        packet.ftrace_events.cpu = cpuid
        cpus[cpuid] = packet
        return cpus[cpuid]

    cpus_last_pid = {}

    def get_cpu_last_pid(cpuid):
        if cpuid in cpus_last_pid:
            return cpus_last_pid[cpuid]
        return 0

    def set_cpu_last_pid(cpuid, last_pid):
        cpus_last_pid[cpuid] = last_pid

    for sample in events:
        if sample["name"] == "svInit":
            with scoping():
                packet = trace.packet.add()
                packet.ftrace_events.cpu = sample["core_id"]
                add_cpu_wakeup(packet,int(sample["ts"] * 1000000000), sample["core_id"] )
                # with scoping():
                #     event = packet.ftrace_events.event.add()
                #     event.timestamp = int(sample["ts"] * 1000000000)
                #     event.pid = 0
                #     event.cpu_idle.state = 0
                #     event.cpu_idle.cpu_id =sample["core_id"]
                with scoping():
                    event = packet.ftrace_events.event.add()
                    event.timestamp = int(sample["ts"] * 1000000000)
                    event.pid = 0
                    event.cpu_frequency.state = int(sample["params"]["cpu_freq"] / 1000)
                    event.cpu_frequency.cpu_id = sample["core_id"]
        elif sample["name"] == "svSysDesc":
            desc = sample["params"]["desc"]
            descitems = desc.split(",")
            for item in descitems:
                itemparts = item.split("=")
                if itemparts[0] == "N": # application name
                    system_info_packet.system_info.utsname.version = itemparts[1]
                elif itemparts[0] == "D": # device
                    system_info_packet.system_info.utsname.machine = itemparts[1]
                elif itemparts[0].startswith("I"): # interrupt information
                    packet = get_cpu(sample["core_id"])
                    with scoping():
                        event = packet.ftrace_events.event.add()
                        event.timestamp = int(sample["ts"] * 1000000000)
                        event.pid = 1
                        event.print.buf = "I|" + str(sample["core_id"]) + "|" + desc
                    interrupt_name = str(sample["core_id"]) + "/" + itemparts[0][1:] + "/" + itemparts[1]
                    interrupt_number = (sample["core_id"] * 100) + int(itemparts[0][2:])

                    add_task_info(int(sample["ts"] * 1000000000),interrupt_number, 0, interrupt_name)
        elif sample["name"] == "svTaskInfo":
            add_task_info(int(sample["ts"] * 1000000000),sample["params"]["tid"], sample["params"]["tid"], sample["params"]["name"])
        elif sample["name"] == "svStackInfo":
            packet = get_cpu(sample["core_id"])
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = sample["params"]["tid"]
                event.print.buf = "I|" + str(sample["params"]["tid"]) + "|" + "Stack " + str(sample["params"]["sz"]) + " bytes"
        elif sample["name"] == "svTaskStartExec":
            packet = get_cpu(sample["core_id"])
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = sample["params"]["tid"]
                event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
                if event.sched_switch.prev_pid == 0:
                    event.sched_switch.prev_comm = "swapper"
                event.sched_switch.next_pid = sample["params"]["tid"]
                set_cpu_last_pid(sample["core_id"], event.pid)
                # add_cpu_wakeup(packet,event.timestamp, sample["core_id"] )
        elif sample["name"] == "svIsrEnter":
            packet = get_cpu(sample["core_id"])
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = get_cpu_last_pid(sample["core_id"])
                event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
                if event.sched_switch.prev_pid == 0:
                    event.sched_switch.prev_comm = "swapper"
                event.sched_switch.next_pid = (sample["core_id"] * 100) + sample["params"]["irq_num"]
                event.sched_switch.next_comm = "I#" + str(sample["params"]["irq_num"])
                set_cpu_last_pid(sample["core_id"], event.sched_switch.next_pid)
                # add_cpu_wakeup(packet,event.timestamp, sample["core_id"] )
        elif sample["name"] == "svExitIsrToScheduler":
            packet = get_cpu(sample["core_id"])
        
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = get_cpu_last_pid(sample["core_id"])
                event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
                if event.sched_switch.prev_pid == 0:
                    event.sched_switch.prev_comm = "swapper"
                event.sched_switch.next_comm = "swapper"
                event.sched_switch.next_pid = 0
                # add_cpu_idle(packet,event.timestamp, sample["core_id"] )
            # with scoping():
            #     event = packet.ftrace_events.event.add()
            #     event.timestamp = int(sample["ts"] * 1000000000)
            #     event.pid = get_cpu_last_pid(sample["core_id"])
            #     event.sched_process_wait.pid = get_cpu_last_pid(sample["core_id"])
            #     add_cpu_idle(packet,event.timestamp, sample["core_id"] )

                # event = packet.ftrace_events.event.add()
                # event.timestamp = int(sample["ts"] * 1000000000)
                # event.pid = get_cpu_last_pid(sample["core_id"])
                # event.sched_switch.prev_pid = get_cpu_last_pid(sample["core_id"])
                # event.sched_switch.next_comm = "Scheduler"
                # event.sched_switch.next_pid = 0
                # set_cpu_last_pid(sample["core_id"], 0)
        # elif sample["name"] == "svTaskStartReady":
        #     packet = get_cpu(sample["core_id"])
        #     with scoping():
        #         event = packet.ftrace_events.event.add()
        #         event.timestamp = int(sample["ts"] * 1000000000)
        #         event.pid = sample["params"]["tid"]
        #         event.sched_wakeup.pid = sample["params"]["tid"]
        #         event.sched_wakeup.target_cpu = sample["core_id"]
        elif sample["name"] == "svTaskStopReady":
            packet = get_cpu(sample["core_id"])
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = sample["params"]["tid"]
                event.sched_wakeup.pid = sample["params"]["tid"]
                event.sched_wakeup.target_cpu = sample["core_id"]
        elif sample["name"] == "vTaskDelay":
            packet = get_cpu(sample["core_id"])
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = get_cpu_last_pid(sample["core_id"])
                event.sched_process_wait.pid = get_cpu_last_pid(sample["core_id"])
        elif sample["name"] == "vTaskDelete":
            packet = get_cpu(sample["core_id"])
            with scoping():
                event = packet.ftrace_events.event.add()
                event.timestamp = int(sample["ts"] * 1000000000)
                event.pid = sample["params"]["xTaskToDelete"]
                event.sched_process_exit.pid = sample["params"]["xTaskToDelete"]
        elif sample["name"] == "svIdle":
            packet = get_cpu(sample["core_id"])
            add_cpu_idle(packet,int(sample["ts"] * 1000000000),sample["core_id"] )

    print("Generated", len(trace.packet), 'packets')

    return trace

def trace_to_json(trace):
    return json.dumps(MessageToDict(trace))

def serialize_trace(trace):
    return perfetto.perfetto_trace_pb2.Trace.SerializeToString(trace)

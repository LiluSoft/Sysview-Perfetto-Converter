
def normalize_event(evt, params):
    return {
        'id':evt.id, 
        'ts':evt.ts, 
        'core_id':evt.core_id, 
        'name':evt.name, 
        'plen':evt.plen,
        'params':params
    }



def is_same_evt(evt1, evt2):
    if (evt1 == None or evt2 == None):
        return False
    if evt1["name"] == evt2["name"] and evt1["core_id"] == evt2["core_id"] and evt1["params"] == evt2["params"]:
        return True
    return False

def process(events):
    last_event = None
    skip_count = 0

    processed_events = []

    for evt in events:
        params = {}
        for p in evt.params:
            params[p] = evt.params[p].value
        
        normalized_event = normalize_event(evt, params)

        if is_same_evt(last_event, normalized_event):
            # nop
            skip_count = skip_count + 1
        else:
            if skip_count > 0:
                # print("skipping", skip_count)
                last_event_end = last_event
                if (last_event_end != None):
                    last_event_end["name"] = last_event_end["name"] + "End"
                    processed_events.append(last_event_end)
            processed_events.append(normalized_event)
            skip_count = 0
        last_event = normalized_event
    return processed_events


def compute_stats(store):
    parts = []
    for part in store.items:
        parts.append(part.tracker_array)
    pph = (len(parts) / parts[len(parts)-1][9]) * 3600
    print "PPH: {:3.2f}".format(pph)

def session_status_changed(session, status):
    print("Trading session status: " + str(status))

def time_frame_to_hours(time_frame):
    time_frame_map = {
        "M1": 1/60, "M5": 5/60, "M15": 15/60, "M30": 30/60,
        "H1": 1, "H4": 4, "D1": 24, "W1": 24 * 7, "MN1": 24 * 30
    }
    return time_frame_map.get(time_frame.upper(), 1)



def nego_lane_change():
    pass

def nego_lane_merge():
    pass

def nego_emergency_vehicle():
    pass

def loop_planning_main():
    egoShouldStop: bool = True
    
    while True:
        if obu.emergencyMsg:
            nego_emergency()


def plan_unprotected_left_turn():
    pass

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
            
        if ego.turnType is TURNTYPE.UNPROTECTED_LEFT_TURN:
            if obu.turnMsg is True:
                egoShouldStop = False
            elif obu.turnMsg is False:
                egoShouldStop = True
            else:
                egoShouldStop = plan_unprotected_left_turn()

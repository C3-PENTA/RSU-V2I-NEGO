

def loop_planning_main():
    egoShouldStop: bool = True
    
    while True:
        if obu.emergencyMsg:
            nego_emergency()
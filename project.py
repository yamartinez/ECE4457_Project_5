#!/usr/bin/env python3

import random
import sys
import time
import threading
import queue

import access_point
import mac

# Handle command line arguments.
if len(sys.argv) != 5:
    print('Usage: {} <# stations> <pkts/s> <pkts> <mac>'.format(sys.argv[0]))
    sys.exit(1)

NUMBER_STATIONS = int(sys.argv[1])
PACKETS_PER_SECOND = float(sys.argv[2])
PACKETS_TO_RECEIVE = int(sys.argv[3])
MAC = sys.argv[4]

mac_protocol = mac.NullMac
if MAC == 'YourMac':
    mac_protocol = mac.YourMac

goal_time = ((PACKETS_TO_RECEIVE / PACKETS_PER_SECOND) * NUMBER_STATIONS) / 10

print('Running Simulator. Settings:')
print('  Number of stations: {}'.format(NUMBER_STATIONS))
print('  Packets / second:   {}'.format(PACKETS_PER_SECOND))
print('  MAC Protocol:       {}'.format(mac_protocol))
print('  Goal Time:          {}'.format(goal_time))


# Track the start time of running the simulator.
start = time.time()

# Need a queue to simulate wireless transmissions to the access point.
q_to_ap = queue.Queue()
station_queues = []

# Need to know where each station is.
station_locations = {}

# Setup and start each wireless station.
for i in range(NUMBER_STATIONS):
    # Get random x,y for station.
    x = round((random.randint(1, 500) / 10.0) - 10.0, 1)
    y = round((random.randint(1, 500) / 10.0) - 10.0, 1)
    station_locations[i] = (x, y)

    q = queue.Queue()
    station_queues.append(q)
    t = mac_protocol(i, q_to_ap, q, PACKETS_PER_SECOND)
    t.daemon = True
    t.start()

    # Delay to space stations
    time.sleep((1.0/PACKETS_PER_SECOND) / NUMBER_STATIONS)

print('Setup {} stations:'.format(NUMBER_STATIONS))
for i,location in station_locations.items():
    print('  Station {}: x: {}, y: {}'.format(i, location[0], location[1]))

# And run the access point.
ap = access_point.AccessPoint(q_to_ap, station_queues, station_locations, PACKETS_TO_RECEIVE)
ap.run()

# When the access point stops running then we have received the correct number
# of packets from each station.
end = time.time()

print('Took {} seconds'.format(end-start))
print('Goal Time: {} seconds'.format(goal_time))
sys.exit(0)

from core.nodes.computing_node import ComputingNode
from core.nodes.transmission_node import TransmissionNode


def case_edge_computing():

    print("-- EC Case")
    data_size = 100 #Mb

    user_time_cost = 0
    user_energy_cost = 0

    obc = ComputingNode(speed=30.0, phi=0.9)
    user_time_cost += obc.time_cost(data_size)
    user_energy_cost += obc.energy_cost(data_size, energy_uptime=5, energy_io=25)
    d_out = obc.process(data_size)

    isl = TransmissionNode(speed=20.0)
    user_time_cost += isl.time_cost(d_out)
    user_energy_cost += isl.energy_cost(d_out, energy=5, distance=100)
    d_out = isl.process(d_out)

    print("User costs:")
    print("Time: " + str(user_time_cost) + " Energy: " + str(user_energy_cost))

    ec_time_cost = 0
    ec_energy_cost = 0

    edge_computer = ComputingNode(speed=300.0, phi=0.4)
    ec_time_cost += edge_computer.time_cost(d_out)
    ec_energy_cost += edge_computer.energy_cost(d_out, energy_uptime=5, energy_io=25)
    d_out = edge_computer.process(d_out)

    ground_link = TransmissionNode(speed=10.0)
    ec_time_cost += ground_link.time_cost(d_out)
    ec_energy_cost += ground_link.energy_cost(d_out, energy=5, distance=700)
    d_out = ground_link.process(d_out)

    print("Edge costs:")
    print("Time: " + str(ec_time_cost) + " Energy: " + str(ec_energy_cost))

    print("Total costs:")
    print("Time: " + str(user_time_cost + ec_time_cost) +
          " Energy: " + str(user_energy_cost + ec_energy_cost))


def case_standalone():
    #data_size = bitmath.Mb(100)
    data_size = 100 #Mb

    time_cost = 0
    energy_cost = 0

    obc = ComputingNode(speed=30.0, phi=0.9)
    time_cost += obc.time_cost(data_size)
    energy_cost += obc.energy_cost(data_size, energy_uptime=5, energy_io=25)
    d_out = obc.process(data_size)

    ground_link = TransmissionNode(speed=10.0)
    time_cost += ground_link.time_cost(d_out)
    energy_cost += ground_link.energy_cost(d_out, energy=5, distance=700)
    d_out = ground_link.process(d_out)

    print("-- Standalone case:")
    print("Time: " + str(time_cost) + " Energy: " + str(energy_cost))

case_standalone()
case_edge_computing()
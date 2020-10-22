import simpy
import random
import statistics
import matplotlib.pyplot as plt

"""
Purpose -- Compare the average wait time for a customer at a grocery store
between having them wait in one line vs. a line for each cash register.

"""

"""

Below is the code for simulating a grocery store with individiual lines
for each register.

"""

number_of_trials = int(input("Number of trials to be tested:"))
class Customer(object):
    """Customer class which is created with a random number of items in
    in between 1 and 20"""

    def __init__(self):

        self.items = random.randint(1,20)


class Store_m_lines(object):
    """
    The store class is the environment for the simulation and contains the
    resources which are used (registers.) This class simulates a store with a
    line for each register. This is done by creating a list of identical resources.
    When a customer requests a register, they find the shortest line and wait
    in that line.

    The check out time is set by the function check_out_customer. The formula
    for the time is takes to check out was chosen to be (# of items)/4 + 2.
    The first term represents the check out time per item a customer has. The
    second term represents the time it takes to pay.
     """

    def __init__(self, env, number_of_registers):

        self.env = env
        self.registers = [simpy.Resource(env, 1) for i in range(number_of_registers)]

    def check_out_customer(self, customer):

        yield self.env.timeout((customer.items/4) + 2)


def shortest_line(registers):
    min_len = len(registers[0].queue) + len(registers[0].users) #initalize length as first line
    j = 0  #initalize the chosen line as the first line
    for i in range(len(registers)):
        if min_len > len(registers[i].queue) + len(registers[i].users):
            min_len = len(registers[i].queue) + len(registers[i].users)
            j = i
    return j   #return the index of the shortest line


def go_to_store_m_lines(env, customer, store_m_lines):

    arrival_time = env.now


    x = shortest_line(store_m_lines.registers) #customer finds the shortest line

    with store_m_lines.registers[x].request() as request:

        yield request
        time_spent = env.now - arrival_time
        yield env.process(store_m_lines.check_out_customer(customer))

    checkout_times.append(time_spent)
    items.append(customer.items)



def run_store_m_lines(env, number_of_registers, customer_freq):

    store_m_lines = Store_m_lines(env, number_of_registers)
    customers = [Customer() for i in range(20)]

    for customer in customers:

        env.process(go_to_store_m_lines(env, customer, store_m_lines))

    while True:
        yield env.timeout(customer_freq)

        new_customer = Customer()
        env.process(go_to_store_m_lines(env, new_customer, store_m_lines))

average_wait_times_mult = []

for j in range(1,20):

    checkout_times = []
    items = []

    for i in range(number_of_trials):

        env = simpy.Environment()
        env.process(run_store_m_lines(env, 3, 0.5 + (3.5*j/20)))
        env.run(until=100)

    average_wait_times_mult.append([statistics.mean(checkout_times)])



"""
Below is the code for simulating a grocery store with one line which funnels
into all of the registers.

"""





class Store_one_line(object):
    """
    This class functions the same as the store class above except that there is
    only one resource but it has a higher capacity. When a customer requests a
    register, they get in line for all of the registers.
    """

    def __init__(self, env, number_of_registers):

        self.env = env
        self.register =  simpy.Resource(env, number_of_registers)

    def check_out_customer(self, customer):

        yield self.env.timeout((customer.items/4) + 2)



def go_to_store_one_line(env, customer, store_one_line):

    arrival_time = env.now

    with store_one_line.register.request() as request:

        yield request
        time_spent = env.now - arrival_time
        yield env.process(store_one_line.check_out_customer(customer))


    checkout_times.append(time_spent)
    items.append(customer.items)

def run_store_one_line(env, number_of_registers, customer_freq):

    store_one_line = Store_one_line(env, number_of_registers)
    customers = [Customer() for i in range(20)] # 20 customers in the store at t=0

    for customer in customers:
        env.process(go_to_store_one_line(env, customer, store_one_line))

    while True:
        yield env.timeout(customer_freq) # wait time, customer_freq, then add another customer.

        new_customer = Customer()
        env.process(go_to_store_one_line(env, new_customer, store_one_line))


average_wait_times_single = []

for j in range(1,20):

    checkout_times = []
    items = []

    for i in range(number_of_trials):

        env = simpy.Environment()
        env.process(run_store_one_line(env, 3, 0.5 + (3.5*j/20)))
        env.run(until=100)

    average_wait_times_single.append([statistics.mean(checkout_times)])

print("Average wait times for multiple line simulation: {}".format(average_wait_times_mult))
print("Average wait times for single line simulation: {}".format(average_wait_times_single))




x_data = [0.5 + (3.5*j/20) for j in range(1,20)]

plt.plot(x_data, average_wait_times_single, 'bo' )
plt.plot(x_data, average_wait_times_mult, 'ro')
plt.axis([0.5, 4, -0.5, 40])
plt.ylabel('Average Wait Times')
plt.xlabel('Interval of customer arrival')
plt.show()

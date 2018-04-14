'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import copy

input_file = 'input.txt'

# Implementation of Min Heap data structure

class minHeap:
    def __init__(self):
        # Do not insert to the first location of the following list,
        # Easier to compute the indices
        self.binary_heap = [Process(0, 0, 0)]
        self.size = 0


    def insert(self, proc):
        self.binary_heap.append(proc)
        self.size += 1
        last_i = self.size
        self.bubble_up(last_i)

    def removeMin(self):
        if self.size == 0:
            return None
        self.binary_heap[0] = self.binary_heap[1]
        self.binary_heap[1] = self.binary_heap[self.size]
        self.binary_heap.pop()
        self.size -= 1
        self.bubble_down(1)
        return self.binary_heap[0]

    def peek(self):
        if self.size == 0:
            return None
        return self.binary_heap[1]
        
    # Use the following bubble_up and bubble_down to maintain the minHeap properties
    def bubble_up(self, last_i):
        if last_i == 1:
            return

        parent_i = last_i / 2
        if self.binary_heap[parent_i].remaining_time > self.binary_heap[last_i].remaining_time:
            tmp = self.binary_heap[parent_i]
            self.binary_heap[parent_i] = self.binary_heap[last_i]
            self.binary_heap[last_i] = tmp
            self.bubble_up(parent_i)

    def bubble_down(self, parent_i):
        left_i = parent_i * 2
        right_i = parent_i * 2 + 1

        left_diff = 0
        right_diff = 0

        if left_i <= self.size:
            left_diff = self.binary_heap[parent_i].remaining_time - self.binary_heap[left_i].remaining_time
        if right_i <= self.size:
            right_diff = self.binary_heap[parent_i].remaining_time - self.binary_heap[right_i].remaining_time

        if left_diff > 0 and left_diff > right_diff:
            tmp = self.binary_heap[parent_i]
            self.binary_heap[parent_i] = self.binary_heap[left_i]
            self.binary_heap[left_i] = tmp
            self.bubble_down(left_i)

        if right_diff > 0 and right_diff > left_diff:
            tmp = self.binary_heap[parent_i]
            self.binary_heap[parent_i] = self.binary_heap[right_i]
            self.binary_heap[right_i] = tmp
            self.bubble_down(right_i)

def ds_test():
    print("Testing Min Heap data structure...")
    arrived_heap = minHeap()
    arrived_heap.insert(Process(3, 0, 63))
    arrived_heap.insert(Process(2, 5, 22))
    arrived_heap.insert(Process(2, 10, 21))
    arrived_heap.insert(Process(3, 15, 28))
    arrived_heap.insert(Process(2, 20, 8))
    arrived_heap.insert(Process(2, 45, 9))
    arrived_heap.insert(Process(2, 45, 20))
    for process in arrived_heap.binary_heap:
        print(process)


class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.completed = False
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d, remaining_time %d]'%(self.id, self.arrive_time, self.burst_time, self.remaining_time))

    def save_result(self, current_time, schedule, remaining_num, total_wait_time):
        if self.remaining_time == 0 and not self.completed:
            wait_time = current_time - self.burst_time - self.arrive_time
            total_wait_time += wait_time
            remaining_num -= 1
            self.completed = True
            schedule.append((current_time, self.id))
            print("Process %d total wait time: %d" % (self.id, wait_time))
            print("Remaining processes: %d" % remaining_num)

        if self.remaining_time != 0:
            schedule.append((current_time, self.id))

        return current_time, schedule, remaining_num, total_wait_time

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    process_list = copy.deepcopy(process_list)
    schedule = list()
    current_time = 0
    total_wait_time = 0
    idle = False

    i = 0
    n = len(process_list)
    remaining_num = n
    last_seen_remaining_num = 0

    print("Remaining processes: %d" % remaining_num)

    while remaining_num > 0:
        if process_list[i].remaining_time > time_quantum:
            current_time += time_quantum
            process_list[i].remaining_time -= time_quantum
            last_seen_remaining_num += 1

        elif process_list[i].remaining_time <= time_quantum and process_list[i].remaining_time > 0:
            current_time += process_list[i].remaining_time
            process_list[i].remaining_time = 0

        if process_list[i].remaining_time == 0 and not process_list[i].completed:
            wait_time = current_time - process_list[i].burst_time - process_list[i].arrive_time
            total_wait_time += wait_time
            remaining_num -= 1
            process_list[i].completed = True
            print("Process %d total wait time: %d" % (process_list[i].id, wait_time))
            schedule.append((current_time, process_list[i].id))
            print("Remaining processes: %d" % remaining_num)

        if process_list[i].remaining_time != 0:
            schedule.append((current_time, process_list[i].id))

        i += 1

        if i > n - 1:
            i = 0

        if current_time < process_list[i].arrive_time:
            if last_seen_remaining_num > 0:
                print("Continue working on incomplete processes...")
                last_seen_remaining_num = 0
                i = 0
            else:
                interval_by_next_arrival = process_list[i].arrive_time - current_time
                print("Processor being idle for %d burst time..." % interval_by_next_arrival)
                idle = True

        if idle:
            print("New processes arriving...")
            current_time = process_list[i].arrive_time
            idle = False

    average_wait_time = total_wait_time/float(n)
    return schedule, average_wait_time

def SRTF_scheduling(process_list):
    process_list = copy.deepcopy(process_list)
    process_heap = minHeap()
    schedule = list()
    current_time = 0
    total_wait_time = 0
    idle = False

    i = 0
    n = len(process_list)
    remaining_num = n
    print("Remaining processes: %d" % remaining_num)
    while remaining_num > 0:

        if i < n - 1:

            next_i = i + 1
            interval_by_next_arrival = process_list[next_i].arrive_time - current_time
            process = None

            # Make sure the next process will arrive only after the is-about-to-execute process has completed.
            if interval_by_next_arrival >= process_list[i].remaining_time and process_list[i].remaining_time > 0:
                # Make sure the remaining_time of the is-about-to-execute process is less than or equal to the min in the heap.
                process = process_heap.peek()
                if process == None or process_list[i].remaining_time <= process.remaining_time:
                    process = process_list[i]
                    current_time += process.remaining_time
                # Make sure that the processor will execute the min in the heap, saving the is-about-to-execute process.
                elif process != None and process_list[i].remaining_time > process.remaining_time:
                    process = process_heap.removeMin()
                    current_time += process.remaining_time
                    process_heap.insert(process_list[i])

                process.remaining_time = 0

            # Make sure the next process will arrive before the is-about-to-execute process has completed.
            if interval_by_next_arrival < process_list[i].remaining_time:
                process = process_heap.peek()
                if process == None or process_list[i].remaining_time <= process.remaining_time:
                    process = process_list[i]
                    process.remaining_time -= interval_by_next_arrival
                    current_time += interval_by_next_arrival
                # Make sure that the processor will execute the min in the heap, saving the is-about-to-execute process.
                elif process != None and process_list[i].remaining_time > process.remaining_time:
                    if interval_by_next_arrival < process.remaining_time:
                        process.remaining_time -= interval_by_next_arrival
                        current_time += interval_by_next_arrival
                    else:
                        process = process_heap.removeMin()
                        current_time += process.remaining_time
                        process.remaining_time = 0

                process_heap.insert(process_list[i])

            current_time, schedule, remaining_num, total_wait_time = process.save_result(current_time, schedule, remaining_num, total_wait_time)

            i += 1

            while current_time < process_list[i].arrive_time:
                interval_by_next_arrival = process_list[i].arrive_time - current_time
                if process_heap.size > 0:

                    print("Continue working on incomplete processes...")
                    process = process_heap.peek()
                    if interval_by_next_arrival < process.remaining_time:
                        exec_time = interval_by_next_arrival
                        current_time += exec_time
                        process.remaining_time -= exec_time

                    elif interval_by_next_arrival >= process.remaining_time:
                        process = process_heap.removeMin()
                        current_time += process.remaining_time
                        process.remaining_time = 0
                    current_time, schedule, remaining_num, total_wait_time = process.save_result(current_time, schedule, remaining_num, total_wait_time)

                else:
                    print("Processor being idle for %d burst time..." % interval_by_next_arrival)
                    idle = True
                    break

            if idle:
                print("New processes arriving...")
                current_time = process_list[i].arrive_time
                idle = False
        # No more incoming processes, only the remaining processes in the heap
        # Execute them according to their shortest remaining time
        if i == n - 1:
            process_heap.insert(process_list[i])
            while process_heap.size > 0:
                process = process_heap.removeMin()
                current_time += process.remaining_time
                wait_time = current_time - process.burst_time - process.arrive_time
                process.remaining_time = 0
                current_time, schedule, remaining_num, total_wait_time = process.save_result(current_time, schedule, remaining_num, total_wait_time)

    average_wait_time = total_wait_time/float(n)
    return schedule, average_wait_time
def SJF_scheduling(process_list, alpha):
    return (["to be completed, scheduling SJF without using information from process.burst_time"],0.0)


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

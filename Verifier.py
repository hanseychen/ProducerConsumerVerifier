import os
import re
import subprocess
import sys
import threading


def check_output(output_file):
    """Check the correctness of the output trace."""
    with open(output_file) as f:
        trace = f.readlines()
        produced = []
        consumed = []

        # Parse the output to get the produced and consumed objects
        for line in trace:
            line = line.lower()
            element = re.match('(producer produced )([0-9]+)', line)
            if element:
                produced.append(element.group(2))
            element = re.match('(consumer consumed )([0-9]+)', line)
            if element:
                consumed.append(element.group(2))

        # Check if the result is empty
        if len(produced) == 0 or len(consumed) == 0:
            subprocess.call("echo \"Empty.\" > " + output_file[:-3] + "result",
                            shell=True)
            return


        # Check for over-consumed and over-produced
        if len(produced) - len(consumed) > 5 or len(consumed) > len(produced):
            subprocess.call("echo \"Wrong: Produced " + str(len(produced)) +
                            " items but consumed " + str(len(consumed)) +
                            " items.\" > " + output_file[:-3] + "result",
                            shell=True)
            return

        # Check for order mismatch
        mismatched_index = -1
        for i in range(len(consumed)):
            if produced[i] != consumed[i]:
                mismatched_index = i
                break
        if mismatched_index == -1:
            subprocess.call("echo \"Correct.\" > " + output_file[:-3] + "result",
                            shell=True)
            return

        # Maybe the buffer is implemented as a stack.
        stack = []
        i = 0
        for line in trace:
            line = line.lower()
            element = re.match('(producer produced )([0-9]+)', line)
            if element:
                stack.append(element.group(2))
            else:
                element = re.match('(consumer consumed )([0-9]+)', line)
                if element:
                    i += 1
                    if len(stack) == 0 :
                        subprocess.call("echo \"Wrong: Item " + str(element.group(2)) +
                                        " consumed before anything is produced.\" > " +
                                        output_file[:-3] + "result",
                                        shell=True)
                        return
                    just_produced = stack.pop()
                    if element.group(2) != just_produced:
                        subprocess.call("echo \"Wrong: The " + str(i) + " item consumed is " +
                                        element.group(2) + ". But the item just produced is " +
                                        just_produced + ".\" > " + output_file[:-3] + "result",
                                        shell=True)
                        return

        subprocess.call("echo \"Stack.\" > " + output_file[:-3] + "result",
                        shell=True)


def verify_one(run_time, pro_cnt, con_cnt):
    """Verify one submission against one test scenario."""
    output_file = "./output-" + str(run_time) + "-" + str(pro_cnt) + "-" + str(con_cnt) + ".txt"
    if not os.path.exists('./lab2'):
        return
    subprocess.call("./lab2 " + str(run_time) + " " + str(pro_cnt) + " " + str(con_cnt) +
                    " > " + output_file, shell=True)
    check_output(output_file)


def verify(path):
    """Verify the correctness of the submitted programs.
    The submitted programs are many implementations of the producer-consumer model."""
    cnt = 0
    folders = os.listdir(path)
    for folder in folders:
        dir_path = path + "/" + folder
        if not os.path.isdir(dir_path):
            continue
        print("running " + folder)
        os.chdir(dir_path)
        # Low contention scenario
        t1 = threading.Thread(target=verify_one, args=(10, 1, 1,))
        t1.start()
        print("Start low contention test for " + folder)
        # Mediate contention scenario
        t2 = threading.Thread(target=verify_one, args=(10, 5, 5,))
        t2.start()
        print("Start mediate contention test for " + folder)
        # High contention scenario
        t3 = threading.Thread(target=verify_one, args=(10, 100, 100,))
        t3.start()
        print("Start high contention test for " + folder)
        t1.join()
        print("Low contention test ends.")
        t2.join()
        print("Mediate contention test ends.")
        t3.join()
        print("High contention test ends.")


if __name__ == '__main__':
    verify(sys.argv[1])

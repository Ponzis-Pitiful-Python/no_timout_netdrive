# Program to prevent disconnect from netdrive due to inactivity timeout.

import os
import time
import subprocess
import sys


def print_ts(message):
    print("[%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message))


def run(interval, command):
    print_ts("-" * 50)
    print_ts("Command %s" % command)
    print_ts("Starting every %s seconds." % interval)
    print_ts("-" * 50)

# mounts netdrive, waits 5 sec, then runs ls to check if netdrive is mounted
# Change if your method of connecting to netdrive is different
    mount_command = 'sshfs -o umask=113 prd-kb-classic-util01.dc2.lan:/u1/netdrive ~/netdrive && echo "mounting-debug"'
# change this to the path to your netdrive mount
    count_files = 'ls -1 /home/ponzi/netdrive/ | wc -l'

    subprocess.call(mount_command, shell=True)
    print('Mounting netdrive...')

    time.sleep(5)
    print('Number of files in netdrive. This should NOT be 0!')
    subprocess.call(count_files, shell=True)

    count = 0
    file_number = 20
    recon_tries = 0

    while count < 32:
        try:
            # sleep for the remaining seconds of interval
            time_remaining = interval - time.time() % interval
            print_ts("Sleeping until %s (%s seconds)..." % ((time.ctime(time.time() + time_remaining)), time_remaining))
            time.sleep(time_remaining)
            print_ts("Starting command.")

# test to see if netdrive mounted
            the_output = subprocess.check_output('ls -1 /home/ponzi/netdrive/ | wc -l', shell=True)
            print('Number of files in dir is: ', int(the_output))
            time.sleep(1)
            if int(the_output) < file_number:
                print('netdrive is not mounted!!!')
                time.sleep(4)

# Attempt to reconnect to netdrive 3x then quit program if not successful.
                while recon_tries < 5 and int(the_output) < file_number:
                    the_output = subprocess.check_output('ls -1 /home/ponzi/netdrive/ | wc -l', shell=True)
                    print('Attempting to reconnect to netdrive.')
                    subprocess.call(mount_command, shell=True)
                    time.sleep(1)
                    print('Number of reconnect tries: ', (recon_tries))
                    time.sleep(5)
                    if recon_tries == 4:
                        sys.exit()
                    recon_tries += 1

            # execute the command
            status = os.system(command)
            print_ts("-" * 50)
            print_ts("Command status = %s." % status)
            count += 1
            print("Number of repetitions:", (count))
        except Exception as e:
            print(e)

# unmounts netdrive after loop exits
    time.sleep(2)
# change /home/ponzi/netdrive to your dir path
    umount_command = 'fusermount -u /home/ponzi/netdrive'
    subprocess.call(umount_command, shell=True)
    time.sleep(2)
    print('netdrive is unmounted')

if __name__ == "__main__":
    interval = 900
# Change to your path to netdrive. Change"foo" to something unique, or there could be issues
# with permissions and or collisions.
    command = r"touch /home/ponzi/netdrive/testitfoo"
    run(interval, command)

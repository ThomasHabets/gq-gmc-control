#!/usr/bin/env python3
"""
Parse a binary dump of a GQ GMC 500+.

$ ./gq-gmc-control.py -p /dev/ttyUSB0 --data
$ ./parse.py <the .bin file> | awk -F, '{print $3}'  > b
$ gnuplot
gnuplot> plot 'b' w l
"""

import sys

COMMAND = 0x55
COMMAND2 = 0xaa

COMMAND_COUNT_TYPE = 0x00
COMMAND_LARGE_NUM = 0x01
COMMAND_UNKNOWN5 = 0x05


def parse(fn):
    fin = open(fn, 'rb')

    marker = 0
    line = []
    samples = []
    while True:
        ch = fin.read(1)
        if len(ch) == 0:
            break
        ch = ch[0]

        if marker == COMMAND2:
            marker = 0
            if ch == COMMAND_COUNT_TYPE:
                do_print = True
                if not line:
                    do_print = False
                if len(samples) > 10 and sum(samples) > 0:
                    line.append(str(float(sum(samples))/len(samples) * 60))
                    line.extend([str(x) for x in samples])
                else:
                    do_print = False
                samples = []
                if do_print:
                    print(','.join(line))
                data = fin.read(9)
                if len(data) < 9:
                    break
                mode = data[8]
                if mode == 1:
                    mode = 'CPS'
                else:
                    print('unknown')
                line = ['20%02d/%02d/%02d %02d:%02d:%02d,%s' %
                        (data[0], data[1], data[2], data[3],
                         data[4], data[5], mode)]
            elif ch == COMMAND_LARGE_NUM:
                fin.read(2)
                continue
            elif ch == COMMAND_UNKNOWN5:
                continue
            else:
                print("Unknown command %d" % ch)
                exit(1)
                
        if marker == COMMAND:
            if ch == COMMAND2:
                marker = COMMAND2
                continue
            else:
                break
        
        if ch == COMMAND:
            marker = COMMAND
            continue
        samples.append(ch)

def main():
    parse(sys.argv[1])

if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import argparse
import inspect
import zmq
import pynput


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--address',
        required=True,
        help="Server address, format: 'tcp://<host>:<port>",
    )
    parser.add_argument(
        '--key-single',
        help="Which key to press upon receiving a single pedal press.",
        default="down",
    )
    parser.add_argument(
        '--key-double',
        help="Which key to press upon receiving a double pedal press.",
        default="up",
    )
    args = parser.parse_args()

    ctx = zmq.Context()
    socket = ctx.socket(zmq.SUB)
    # Subscribe to all topics (none specified on server):
    socket.setsockopt(zmq.SUBSCRIBE, b"")

    print("Connecting…")
    socket.connect(args.address)
    print(f"Connection to {args.address} established")

    keyboard = pynput.keyboard.Controller()

    key_single = args.key_single
    key_double = args.key_double
    key_attributes = dict(inspect.getmembers(
        pynput.keyboard.Key,
        lambda a: not inspect.isroutine(a),
    ))
    if len(key_single) > 1:
        key_single = key_attributes[key_single]
    if len(key_double) > 1:
        key_double = key_attributes[key_double]

    print("Waiting for messages")
    while True:
        msg = socket.recv()
        print(msg)
        num_presses = int(msg)
        if num_presses == 1:
            keyboard.press(key_single)
            keyboard.release(key_single)
        elif num_presses == 2:
            keyboard.press(key_double)
            keyboard.release(key_double)
        else:
            print(f"Received unrecognized message: \"{msg}\"")


if __name__ == '__main__':
    main()

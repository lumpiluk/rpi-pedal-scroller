#!/usr/bin/env python3

"""
Sends pedal presses and double presses via ZeroMQ.

Connect one cable to GND and one to GPIO17.
"pressed" and "released" are reversed on input, but sent correctly
to the connected client.
"""

import time
import argparse
import gpiozero
import zmq


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=33777)
    parser.add_argument(
        '--double-press-timeout',
        type=float,
        help="Maximum time in seconds for a double press. "
             "Default: 0.35 s.",
        default=0.3,
    )
    args = parser.parse_args()

    btn = gpiozero.Button(17)

    # zmq setup:
    ctx = zmq.Context()
    socket = ctx.socket(zmq.PUB)
    socket.bind(f"tcp://*:{args.port}")

    print(f"Ready. Publishing on tcp://*:{args.port}")

    while True:
        btn.wait_for_release()  # (inverted -> pressed)
        btn.wait_for_press()  # (inverted -> released)
        btn.wait_for_release(timeout=args.double_press_timeout)
        num_presses = 1
        if not btn.is_pressed:  # (inverted -> *is* pressed)
            btn.wait_for_press()
            num_presses += 1
        socket.send(str(num_presses).encode())
        print(f"Pressed {num_presses} times.")


if __name__ == '__main__':
    main()

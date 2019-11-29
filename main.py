from mido import MidiFile
import time
import pygame
import time
import pygame.midi
import curses
from multiprocessing import Process, Queue, Event
import time
import math


def process(filename, track_number, q, e, offset):
    pygame.midi.init()
    player= pygame.midi.Output(1)
    player.set_instrument(1,1)

    midifile = MidiFile(filename)
    seconds_per_tick = (500000/midifile.ticks_per_beat) / 1000000
    for i in range(offset):
        seconds_per_tick *= 0.999
    orig_seconds_per_tick = seconds_per_tick

    last_message = None

    try:
        while not e.is_set():
            for message in midifile.tracks[track_number]:
                seconds_per_tick = orig_seconds_per_tick * (1-(math.sin(time.time()) * 0.01))
                if e.is_set():
                    break
                key = None
                try:
                    key = q.get(False)
                except:
                    pass
                if key == ord('a'):
                    seconds_per_tick *= 0.9
                if key == ord('d') :
                    seconds_per_tick *= 1.1
                if key == ord('s'):
                    seconds_per_tick = orig_seconds_per_tick
                if last_message:
                    time.sleep(message.time * seconds_per_tick)
                    if message.type == 'note_on':
                        player.note_on(message.note, message.velocity, 1)
                    if message.type == 'note_off':
                        player.note_off(message.note, message.velocity, 1)
                last_message = message
    finally:
        pygame.quit()

def main():
    filename = 'toto_africa.mid'
    #filename = 'symphony_183_2_(c)ishii.mid'
    filename = "rossini_overture_wtellrecorders.mid"
    filename = "willtell.mid"
    filename = "symphony_9_1_(c)cvikl.mid"
    tracks = {
        1: [ord('a'), ord('A')],
        2: [ord('s'), ord('S')],
        3: [ord('d'), ord('D')],
        4: [ord('f'), ord('F')],
        1: [ord('g'), ord('G')]
    }
    midifile = MidiFile(filename)
    print(vars(midifile))
    queues = {}
    processes = []
    e = Event()
    for index, (t, keys) in enumerate(tracks.items()):
        q = Queue()
        for key in keys:
            queues[key] = q
        p = Process(target=process, args=(filename, t, q, e, index*3))
        p.daemon = True
        p.start()
        processes.append(p)
    try:
        stdscr = curses.initscr()
        curses.noecho()
        stdscr.nodelay(1)
        while True:
            key = stdscr.getch()
            q = queues.get(key)
            if q:
                q.put(key)
            time.sleep(0.1)
    finally:
        e.set()
        for p in processes:
            p.join()
        curses.endwin()

if __name__ =="__main__":
    main()


"""
note_off channel=0 note=59 velocity=0 time=8
{'type': 'note_off', 'time': 8, 'note': 59, 'velocity': 0, 'channel': 0}
note_on channel=0 note=56 velocity=93 time=120
{'type': 'note_on', 'time': 120, 'note': 56, 'velocity': 93, 'channel': 0}
note_on channel=0 note=64 velocity=89 time=16
"""
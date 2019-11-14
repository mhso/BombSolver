from sys import argv
import main
from debug import log

def inspect():
    log("Inspecting bomb...")
    IMAGES = main.inspect_bomb()
    fb, lr, ud = main.partition_sides(IMAGES)
    fb.extend(lr)
    fb.extend(ud)
    return fb

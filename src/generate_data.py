from glob import glob
import main
from debug import log

log("Waiting for user to press S")
main.sleep_until_start()
log("Inspecting bomb...")
IMAGES = main.inspect_bomb()
NUM_IMAGES = len(glob("../resources/training_images/*.png"))
SIDE_PARTITIONS = main.partition_sides(IMAGES)
INDEX = NUM_IMAGES
for side in SIDE_PARTITIONS:
    for img in side:
        img.save(f"../resources/training_images/{INDEX:03d}.png")
        INDEX += 1

log(f"Captured {INDEX-NUM_IMAGES} images. Total images: {INDEX}")

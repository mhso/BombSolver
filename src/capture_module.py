from glob import glob
import main
from time import sleep

#main.sleep_until_start()
sleep(5)
tupl = main.screenshot_module()
PATH = "../resources/misc/"
INDEX = len(glob(PATH + "*.png"))
tupl[0].save(f"{PATH}{INDEX}.png")
print("Captured image of module.")

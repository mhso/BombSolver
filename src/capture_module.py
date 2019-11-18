from glob import glob
import main

main.sleep_until_start()
tupl = main.screenshot_module()
PATH = "../resources/misc/"
INDEX = len(glob(PATH + "*.png"))
tupl[0].save(f"{PATH}{INDEX}.png")
print("Captured image of module.")

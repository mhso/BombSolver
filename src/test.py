import view.overlay as overlay
import main
from model.module_classifier import LABELS

ree = overlay.GUIOverlay()

ree.add_status("module_positions", [main.get_module_coords(x) for x in range(6)])
ree.add_status("module_names", [LABELS[10+x] for x in range(6)])

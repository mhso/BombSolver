from os import system, name

class Progress:
    def __init__(self, max_val, desc="Progres"):
        self.value = 0
        self.max_val = max_val
        self.desc = desc
        self.status = None

    def increment(self, amount=1):
        self.value += amount
        self.print_progress()

    def clear(self):
        if name == 'nt':
            _ = system('cls')
        else:
            system("clear")

    def print_progress(self):
        val = self.value
        ratio = val / self.max_val
        max_labels = 40
        labels = int(ratio * max_labels)
        remaining = max_labels - labels
        print_str = self.desc + ": |" + ("#" * labels) + (" " * remaining) + "|"
        self.clear()
        print(print_str)
        if self.status is not None:
            print(self.status)

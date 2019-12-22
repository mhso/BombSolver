if __name__ == "__main__":
    from time import time, sleep
    import view.overlay

    conn = view.overlay.initialize()

    conn.send(("speedrun_time", time()))

    conn.send(("active", True))

    conn.send(("speedrun_splits", [("first_bomb", 30)]))
    conn.send(("speedrun_splits", [("first_bomb", 30), ("one_step_up", 45)]))
    conn.send(("speedrun_splits", [("first_bomb", 30), ("one_step_up", 45), ("new_old", 100)]))
    conn.send(("module_selected", (825, 388, 4)))
    conn.send(("module_info", (17, "MAZE_2")))
    conn.send(("log", ["Some data", "Some more data", "EVEN more data"]))

    try:
        while True:
            sleep(0.5)
    except KeyboardInterrupt:
        conn.send(("active", False))

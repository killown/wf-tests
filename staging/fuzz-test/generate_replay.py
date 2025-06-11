import random
import sys


def parse_log_for_macros(
    log_file_path, output_script_path, last_n_lines=100, max_speed=0.01, max_views=50
):
    """
    Parses log file for macro IDs and generates a replay script using randomized/fuzz-style logic.
    Each action is followed by a random time.sleep() between 1ms and 50ms.
    """

    # Map macro IDs to template strings
    MACRO_MAP = {
        "MOVE_CURSOR": "self.stipc.move_cursor({x}, {y})",
        "CLICK_BUTTON": 'self.stipc.click_button("BTN_LEFT", "full")',
        "CLICK_AND_DRAG": "self.stipc.click_and_drag({button}, {x1}, {y1}, {x2}, {y2}, True)",
        "PRESS_KEY": 'self.stipc.press_key("{key_combination}")',
        "SET_VIEW_MAXIMIZED": "self.utils.set_view_maximized({view_id})",
        "SET_VIEW_FULLSCREEN": "self.sock.set_view_fullscreen({view_id}, True)",
        "SET_VIEW_MINIMIZED": "self.sock.set_view_minimized({view_id}, {state})",
        "SET_VIEW_STICKY": "self.sock.set_view_sticky({view_id}, {state})",
        "SEND_VIEW_TO_BACK": "self.sock.send_view_to_back({view_id}, {state})",
        "SET_VIEW_ALPHA": "self.sock.set_view_alpha({view_id}, {alpha})",
        "SET_VIEW_TOP_LEFT": "self.utils.set_view_top_left({view_id})",
        "SET_VIEW_TOP_RIGHT": "self.utils.set_view_top_right({view_id})",
        "SET_VIEW_BOTTOM_LEFT": "self.utils.set_view_bottom_left({view_id})",
        "SET_VIEW_RIGHT": "self.utils.set_view_right({view_id})",
        "SET_VIEW_LEFT": "self.utils.set_view_left({view_id})",
        "SET_VIEW_BOTTOM": "self.utils.set_view_bottom({view_id})",
        "SET_VIEW_TOP": "self.utils.set_view_top({view_id})",
        "SET_VIEW_CENTER": "self.utils.set_view_center({view_id})",
        "SET_VIEW_BOTTOM_RIGHT": "self.utils.set_view_bottom_right({view_id})",
        "SET_FOCUS": "self.sock.set_focus({view_id})",
        "CUBE_ACTIVATE": "self.sock.cube_activate()",
        "CUBE_ROTATE_LEFT": "self.sock.cube_rotate_left()",
        "CUBE_ROTATE_RIGHT": "self.sock.cube_rotate_right()",
        "TOGGLE_EXPO": "self.sock.toggle_expo()",
        "SCALE_TOGGLE": "self.sock.scale_toggle()",
        "TOGGLE_SHOWDESKTOP": "self.sock.toggle_showdesktop()",
        "CREATE_WAYLAND_OUTPUT": "self.stipc.create_wayland_output()",
        "DESTROY_WAYLAND_OUTPUT": 'self.stipc.destroy_wayland_output("output-1")',
        "RUN_CMD": 'self.stipc.run_cmd("{command}")',
        "DELAY_NEXT_TX": "self.random_delay_next_tx()",
        "GO_WORKSPACE_SET_FOCUS": "self.utils.go_workspace_set_focus({view_id})",
        "CONFIGURE_VIEW": "self.sock.configure_view({view_id}, {x}, {y}, {width}, {height})",
        "SET_WORKSPACE": "self.sock.set_workspace({'x': 0, 'y': 0}, {view_id}, {output_id})",
    }

    # Step 1: Read last N lines from log file
    macros_found = []
    with open(log_file_path, "r") as f:
        lines = f.readlines()[-last_n_lines:]

    for line in lines:
        if "[macro_id=" not in line:
            continue
        try:
            macro_id = line.split()[-1].split("[macro_id=")[-1].split("]")[0]
            if macro_id in MACRO_MAP:
                macros_found.append((macro_id, MACRO_MAP[macro_id]))
        except Exception:
            continue

    # Step 2: Write the generated script
    with open(output_script_path, "w") as out:
        out.write("from wayfire import WayfireSocket\n")
        out.write("from wayfire.extra.ipc_utils import WayfireUtils\n")
        out.write("from wayfire.extra.stipc import Stipc\n")
        out.write("from random import choice, randint, random, uniform\n")
        out.write("from time import sleep\n")

        out.write("class Replay:\n")
        out.write("    def __init__(self):\n")
        out.write("        self.sock = WayfireSocket()\n")
        out.write("        self.utils = WayfireUtils(self.sock)\n")
        out.write("        self.stipc = Stipc(self.sock)\n")
        out.write(
            "        self.do_not_close_view_id = self.sock.get_focused_view()\n\n"
        )

        out.write("    def test_random_view_id(self):\n")
        out.write("        ids = self.utils.list_ids()\n")
        out.write("        return choice(ids) if ids else None\n\n")

        out.write("    def max_views(self, max_views):\n")
        out.write("        if len(self.sock.list_views()) > max_views:\n")
        out.write("            for view in self.sock.list_views():\n")
        out.write("                if view['id'] == self.do_not_close_view_id['id']:\n")
        out.write("                    continue\n")
        out.write("                self.sock.close_view(view['id'])\n")
        out.write("                if len(self.sock.list_views()) < max_views:\n")
        out.write("                    break\n\n")

        out.write("    def _sum_geometry_resolution(self):\n")
        out.write("        outputs = self.sock.list_outputs()\n")
        out.write("        total_width = 0\n")
        out.write("        total_height = 0\n")
        out.write("        for output in outputs:\n")
        out.write('            total_width += output["geometry"]["width"]\n')
        out.write('            total_height += output["geometry"]["height"]\n')
        out.write("        return total_width, total_height\n")

        out.write("    def random_delay_next_tx(self):\n")
        out.write("        for _ in range(randint(1, 10)):\n")
        out.write("            self.stipc.delay_next_tx()\n\n")

        out.write("    def replay(self):\n")
        out.write(f"        self.max_views({max_views})\n")

        for macro_id, template in macros_found:
            args = {}

            if "{view_id}" in template:
                args["view_id"] = "self.test_random_view_id()"

            if "{x}" in template or "{y}" in template:
                args["x"] = "randint(100, self._sum_geometry_resolution()[0])"
                args["y"] = "randint(100, self._sum_geometry_resolution()[1])"

            if (
                "{x1}" in template
                or "{y1}" in template
                or "{x2}" in template
                or "{y2}" in template
            ):
                args["x1"] = "randint(100, self._sum_geometry_resolution()[0])"
                args["y1"] = "randint(100, self._sum_geometry_resolution()[1])"
                args["x2"] = "randint(100, self._sum_geometry_resolution()[0])"
                args["y2"] = "randint(100, self._sum_geometry_resolution()[1])"
                args["button"] = '"S-BTN_LEFT"'

            if "{button}" in template:
                args["button"] = '"BTN_LEFT"'
                args["state"] = '"full"'

            if "{key_combination}" in template:
                mods = ["A-", "S-", "C-"]
                keys = ["KEY_A", "KEY_B", "KEY_C", "KEY_D", "KEY_E", "KEY_F"]
                key_combo = f'"{random.choice(mods)}{random.choice(keys)}"'
                args["key_combination"] = key_combo

            if "{command}" in template:
                terms = ["xterm", "alacritty", "kitty", "gnome-terminal"]
                args["command"] = f"{random.choice(terms)}"

            if "{state}" in template:
                args["state"] = random.choice(["True", "False"])

            if "{alpha}" in template:
                args["alpha"] = str(round(random.random(), 2))

            if "{output_id}" in template:
                args["output_id"] = "choice(self.utils.list_outputs_ids())"

            if "{width}" in template or "{height}" in template:
                args["width"] = "randint(200, 800)"
                args["height"] = "randint(100, 600)"

            try:
                func_call = template.format(**args)
                out.write("        try:\n")
                out.write(f"            {func_call}  # {macro_id}\n")
                out.write("        except Exception as e:\n")
                out.write("            print(e)\n")
                out.write("            pass\n")
                out.write(
                    f"        sleep(uniform(0.001, {max_speed}))  # Random delay\n"
                )
            except KeyError as e:
                print(f"[ERROR] Missing argument for macro '{macro_id}': {e}")

        out.write("\nif __name__ == '__main__':\n")
        out.write("    r = Replay()\n")
        out.write("    while True:\n")
        out.write("        try:\n")
        out.write("            r.replay()\n")
        out.write("        except:\n")
        out.write("            pass\n")

    print(
        f"Replay script written to '{output_script_path}' with {len(macros_found)} actions."
    )


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python generate_replay.py <log_file_path> <output_script_path> [max_lines: int] [max_speed: float] [max_views: int]"
        )
        sys.exit(1)

    log_file_path = sys.argv[1]
    output_script_path = sys.argv[2]
    last_n_lines = int(sys.argv[3])
    max_speed = float(sys.argv[4])
    max_views = int(sys.argv[5])

    parse_log_for_macros(
        log_file_path,
        output_script_path,
        last_n_lines=last_n_lines,
        max_speed=max_speed,
        max_views=max_views,
    )

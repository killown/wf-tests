import gi
import random

gi.require_version("Gtk", "4.0")
gi.require_version("Gtk4LayerShell", "1.0")
from gi.repository import Gtk, GLib
from gi.repository import Gtk4LayerShell as LayerShell


def spawn_random_window():
    window = Gtk.Window()
    window.set_title("Spam Window")

    # Random size between 1 and 10000
    width = random.randint(100, 1000)
    height = random.randint(100, 1000)
    window.set_default_size(width, height)

    # Initialize LayerShell
    LayerShell.init_for_window(window)
    LayerShell.set_namespace(window, "spam")  # Optional namespace
    LayerShell.set_layer(window, LayerShell.Layer.TOP)

    # Random anchor edges
    for edge in [
        LayerShell.Edge.TOP,
        LayerShell.Edge.BOTTOM,
        LayerShell.Edge.LEFT,
        LayerShell.Edge.RIGHT,
    ]:
        if random.random() > 0.5:
            LayerShell.set_anchor(window, edge, True)

    # Optional margins
    if random.random() > 0.5:
        LayerShell.set_margin(window, LayerShell.Edge.TOP, random.randint(0, 100))
    if random.random() > 0.5:
        LayerShell.set_margin(window, LayerShell.Edge.LEFT, random.randint(0, 100))

    # Show the window
    window.present()

    return False  # For GLib timeout source (not repeating)


def main():
    app = Gtk.Application(application_id="com.example.LayerShellSpam")

    def on_activate(app_window):
        print("Starting spam...")

        # Spam one window every 200ms
        def schedule_next(*_):
            spawn_random_window()
            return True  # Keep source active

        schedule_next()

    app.connect("activate", on_activate)
    app.run(None)


if __name__ == "__main__":
    main()

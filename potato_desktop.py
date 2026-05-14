import random
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from typing import List

from pynput import keyboard


WINDOW_SIZE = 120
GRAVITY = 1.1
BOUNCE_DAMPING = 0.92
HORIZONTAL_SPEED_RANGE = (-4.5, 4.5)
INITIAL_JUMP_RANGE = (-24.0, -16.0)
MIN_HORIZONTAL_SPEED = 1.2
MIN_BOUNCE_SPEED = 10.0
SPAWN_OFFSET = 80
IMAGE_NAME = 'potato.png'


@dataclass
class Velocity:
    dx: float
    dy: float


class PotatoWindow:
    def __init__(self, app: 'PotatoApp', x: int, y: int):
        self.app = app
        self.size = WINDOW_SIZE
        self.root = tk.Toplevel(app.root)
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'white')

        self.canvas = tk.Canvas(
            self.root,
            width=self.size,
            height=self.size,
            bg='white',
            highlightthickness=0,
        )
        self.canvas.pack()

        self.potato_id = self.canvas.create_image(
            self.size // 2,
            self.size // 2,
            image=app.potato_image,
        )

        self.root.geometry(f'{self.size}x{self.size}+{x}+{y}')

        self.v = Velocity(
            dx=random.uniform(*HORIZONTAL_SPEED_RANGE),
            dy=random.uniform(*INITIAL_JUMP_RANGE),
        )

        self.root.bind('<Button-1>', self._spawn_more)

    def _spawn_more(self, _event):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        self.app.create_potato(x + SPAWN_OFFSET, y)
        self.app.create_potato(x - SPAWN_OFFSET, y)

    def step(self):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        x = self.root.winfo_x() + self.v.dx
        y = self.root.winfo_y() + self.v.dy

        self.v.dy += GRAVITY

        if x <= 0:
            x = 0
            self.v.dx *= -1
        elif x + self.size >= screen_w:
            x = screen_w - self.size
            self.v.dx *= -1

        floor_y = screen_h - self.size
        if y >= floor_y:
            y = floor_y
            self.v.dy *= -BOUNCE_DAMPING

            # Keep potatoes moving forever: maintain minimum bounce and drift.
            if abs(self.v.dy) < MIN_BOUNCE_SPEED:
                self.v.dy = -MIN_BOUNCE_SPEED

            if abs(self.v.dx) < MIN_HORIZONTAL_SPEED:
                self.v.dx = random.choice((-1, 1)) * MIN_HORIZONTAL_SPEED

            # Small random impulse on every bounce for varied endless motion.
            self.v.dx += random.uniform(-0.5, 0.5)

        self.root.geometry(f'{self.size}x{self.size}+{int(x)}+{int(y)}')


class PotatoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.potatoes: List[PotatoWindow] = []
        self._pressed_keys = set()
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )

        self.potato_image = self._load_potato_image()

        center_x = self.root.winfo_screenwidth() // 2
        floor_y = self.root.winfo_screenheight() - WINDOW_SIZE
        self.create_potato(center_x, floor_y)

    def _load_potato_image(self) -> tk.PhotoImage:
        image_path = Path(__file__).resolve().parent / IMAGE_NAME
        if not image_path.exists():
            raise FileNotFoundError(f'Image file not found: {image_path}')

        image = tk.PhotoImage(file=str(image_path))
        max_side = max(image.width(), image.height())
        if max_side > WINDOW_SIZE:
            scale = max_side // WINDOW_SIZE + (1 if max_side % WINDOW_SIZE else 0)
            image = image.subsample(scale, scale)

        return image

    def create_potato(self, x: int, y: int):
        self.potatoes.append(PotatoWindow(self, x, y))

    def _on_key_press(self, key):
        self._pressed_keys.add(key)

        is_y = key == keyboard.KeyCode.from_char('y') or key == keyboard.KeyCode.from_char('Y')
        is_shift = keyboard.Key.shift in self._pressed_keys or keyboard.Key.shift_l in self._pressed_keys or keyboard.Key.shift_r in self._pressed_keys

        if is_y and is_shift:
            self.root.after(0, self.stop)

    def _on_key_release(self, key):
        self._pressed_keys.discard(key)

    def run(self):
        self._listener.start()
        self._tick()
        self.root.mainloop()

    def _tick(self):
        for potato in self.potatoes:
            potato.step()
        self.root.after(16, self._tick)

    def stop(self):
        self._listener.stop()
        for potato in self.potatoes:
            potato.root.destroy()
        self.root.quit()


if __name__ == '__main__':
    app = PotatoApp()
    app.run()

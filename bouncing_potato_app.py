import random
import tkinter as tk


class Potato:
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: int = 60):
        self.canvas = canvas
        self.size = size
        self.vx = random.choice([-4, -3, 3, 4])
        self.vy = random.choice([-6, -5, 5, 6])
        self.gravity = 0.35

        body_color = random.choice(["#b07d3b", "#b88a48", "#a87133", "#c49555"])

        left = x - size / 2
        top = y - size / 2
        right = x + size / 2
        bottom = y + size / 2

        self.body = canvas.create_oval(left, top, right, bottom, fill=body_color, outline="#6b4a24", width=2)

        eye_offset_x = size * 0.15
        eye_offset_y = size * 0.12
        eye_size = size * 0.08
        self.eye1 = canvas.create_oval(
            x - eye_offset_x - eye_size,
            y - eye_offset_y - eye_size,
            x - eye_offset_x + eye_size,
            y - eye_offset_y + eye_size,
            fill="black",
        )
        self.eye2 = canvas.create_oval(
            x + eye_offset_x - eye_size,
            y - eye_offset_y - eye_size,
            x + eye_offset_x + eye_size,
            y - eye_offset_y + eye_size,
            fill="black",
        )

        self.items = [self.body, self.eye1, self.eye2]

    def center(self):
        coords = self.canvas.coords(self.body)
        return (coords[0] + coords[2]) / 2, (coords[1] + coords[3]) / 2

    def move(self, width: int, height: int):
        self.vy += self.gravity

        dx = self.vx
        dy = self.vy

        x1, y1, x2, y2 = self.canvas.coords(self.body)

        if x1 + dx <= 0 or x2 + dx >= width:
            self.vx *= -1
            dx = self.vx

        if y1 + dy <= 0:
            self.vy *= -0.9
            dy = self.vy

        if y2 + dy >= height:
            self.vy *= -0.85
            dy = self.vy
            if abs(self.vy) < 2:
                self.vy = random.choice([-8, -7, -6])
                dy = self.vy

        for item in self.items:
            self.canvas.move(item, dx, dy)

    def contains(self, x: float, y: float) -> bool:
        x1, y1, x2, y2 = self.canvas.coords(self.body)
        return x1 <= x <= x2 and y1 <= y <= y2


class PotatoApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Прыгающая картошка")
        self.root.geometry("900x600")
        self.root.configure(bg="#222")

        self.info = tk.Label(
            self.root,
            text="Клик по картошке: +2 новых. Выход: Shift + Y",
            bg="#222",
            fg="white",
            font=("Segoe UI", 11),
        )
        self.info.pack(fill=tk.X, pady=6)

        self.canvas = tk.Canvas(self.root, bg="#1e1e1e", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.potatoes: list[Potato] = []

        self.root.bind("<Shift-Y>", self.exit_app)
        self.canvas.bind("<Button-1>", self.on_click)

        self.root.after(50, self.init_scene)
        self.animate()

    def init_scene(self):
        self.spawn_potato(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2)

    def spawn_potato(self, x: float, y: float):
        self.potatoes.append(Potato(self.canvas, x, y))

    def on_click(self, event):
        for potato in reversed(self.potatoes):
            if potato.contains(event.x, event.y):
                px, py = potato.center()
                self.spawn_potato(px + random.randint(-40, 40), py + random.randint(-40, 40))
                self.spawn_potato(px + random.randint(-40, 40), py + random.randint(-40, 40))
                break

    def animate(self):
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        for potato in self.potatoes:
            potato.move(width, height)
        self.root.after(16, self.animate)

    def exit_app(self, _event=None):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    PotatoApp().run()

from tkinter import *
import random
import pygame
from PIL import Image, ImageTk

GAME_WIDTH = 800
GAME_HEIGHT = 600
SPEED = 150
SPACE_SIZE = 50
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"

class GameObject:
    def __init__(self, canvas, x_axis, y_axis):
        self.canvas = canvas
        self.coordinates = [x_axis, y_axis]

    def get_position(self):
        return self.coordinates

class ImageLoader:
    @staticmethod
    def load_rotated_images(filename):
        base_image = Image.open(filename).resize((SPACE_SIZE, SPACE_SIZE))
        return {
            "up": ImageTk.PhotoImage(base_image),
            "down": ImageTk.PhotoImage(base_image.rotate(180)),
            "left": ImageTk.PhotoImage(base_image.rotate(90)),
            "right": ImageTk.PhotoImage(base_image.rotate(-90))
        }

class Jake(GameObject):
    def __init__(self, canvas):
        super().__init__(canvas, 0, 0)
        self.body_size = BODY_PARTS
        self.coordinates = [[0, 0] for _ in range(self.body_size)]
        self.images = []
        self.current_direction = 'down'

        self.head_images = ImageLoader.load_rotated_images("jake_head.png")
        self.body_images = ImageLoader.load_rotated_images("jake_body.png")
        self.tail_images = ImageLoader.load_rotated_images("jake_bottom.png")

        for index, (x_axis, y_axis) in enumerate(self.coordinates):
            image = self._get_body_part_image(index)
            image_id = canvas.create_image(x_axis, y_axis, image=image, anchor="nw", tag="snake")
            self.images.append(image_id)

    def _get_body_part_image(self, index):
        if index == 0:
            return self.head_images['right']
        elif index == self.body_size - 1:
            return self.tail_images['right']
        return self.body_images['right']

    def set_direction(self, new_direction):
        self.current_direction = new_direction

    def grow(self, x_axis, y_axis):
        self.coordinates.insert(0, (x_axis, y_axis))
        head_image = self.head_images[self.current_direction]
        image_id = self.canvas.create_image(x_axis, y_axis, image=head_image, anchor="nw", tag="snake")
        self.images.insert(0, image_id)

        if len(self.images) > 1:
            self.canvas.itemconfig(self.images[1], image=self.body_images[self.current_direction])
        if len(self.images) >= 2:
            self._update_tail_image()

    def shrink(self):
        self.coordinates.pop()
        self.canvas.delete(self.images.pop())
        if len(self.coordinates) >= 2:
            self._update_tail_image()

    def _update_tail_image(self):
        second_to_last_x, second_to_last_y = self.coordinates[-2]
        last_x, last_y = self.coordinates[-1]

        if second_to_last_x > last_x:
            tail_direction = 'right'
        elif second_to_last_x < last_x:
            tail_direction = 'left'
        elif second_to_last_y > last_y:
            tail_direction = 'down'
        else:
            tail_direction = 'up'

        self.canvas.itemconfig(self.images[-1], image=self.tail_images[tail_direction])

class Food(GameObject):
    def __init__(self, canvas):
        x_axis = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y_axis = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        super().__init__(canvas, x_axis, y_axis)
        self.image = PhotoImage(file="food.png")
        self.image_id = canvas.create_image(x_axis, y_axis, image=self.image, anchor="nw", tag="food")
        canvas.food_image = self.image

def next_turn():
    global score, direction, food

    head_x_axis, head_y_axis = jake.coordinates[0]
    move_map = {'up': (0, -SPACE_SIZE), 'down': (0, SPACE_SIZE), 'left': (-SPACE_SIZE, 0), 'right': (SPACE_SIZE, 0)}
    delta_x, delta_y = move_map[direction]
    new_x_axis = head_x_axis + delta_x
    new_y_axis = head_y_axis + delta_y

    jake.grow(new_x_axis, new_y_axis)

    food_x_axis, food_y_axis = food.get_position()

    if new_x_axis == food_x_axis and new_y_axis == food_y_axis:
        eat_sound.play()
        score += 1
        label.config(text=f"Score:{score}")
        canvas.delete("food")
        food = Food(canvas)
    else:
        jake.shrink()

    if check_collisions():
        game_over()
    else:
        window.after(SPEED, next_turn)

def change_direction(new_direction):
    global direction
    if direction != {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}.get(new_direction):
        direction = new_direction
        jake.set_direction(new_direction)

def check_collisions():
    x_axis, y_axis = jake.coordinates[0]
    return (
        x_axis < 0 or x_axis >= GAME_WIDTH or y_axis < 0 or y_axis >= GAME_HEIGHT or
        (x_axis, y_axis) in jake.coordinates[1:]
    )

def game_over():
    canvas.delete(ALL)
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                       font=('consolas', 70), text="GAME OVER", fill="red", tag="gameover")

window = Tk()
window.title("Snake Game")
window.resizable(False, False)

score = 0
direction = 'down'

label = Label(window, text=f"Score:{score}", font=('consolas', 40))
label.pack()

canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()

background_image = PhotoImage(file="grass_bg.png")
canvas.create_image(0, 0, image=background_image, anchor="nw")
canvas.background = background_image

window.update()
window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + label.winfo_height()}+{int((window.winfo_screenwidth() / 2) - (window.winfo_width() / 2))}+{int((window.winfo_screenheight() / 2) - (window.winfo_height() / 2))}")

for key, direction_key in {'<Left>': 'left', '<Right>': 'right', '<Up>': 'up', '<Down>': 'down'}.items():
    window.bind(key, lambda event, d=direction_key: change_direction(d))

jake = Jake(canvas)
food = Food(canvas)

pygame.mixer.init()
pygame.mixer.music.load("adventure_time_bg_music.wav")
pygame.mixer.music.play(-1)

eat_sound = pygame.mixer.Sound("eat_sound.wav")

next_turn()
window.mainloop()

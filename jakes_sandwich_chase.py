from tkinter import *
import random
import pygame
from PIL import Image, ImageTk

GAME_WIDTH = 800
GAME_HEIGHT = 600
SPEED = 150
SPACE_SIZE = 50
BODY_PARTS = 3
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
        self.direction = 'down'

        self.head = ImageLoader.load_rotated_images("assets/jake_head.png")
        self.body = ImageLoader.load_rotated_images("assets/jake_body.png")
        self.tail = ImageLoader.load_rotated_images("assets/jake_bottom.png")

        for index, (x_axis, y_axis) in enumerate(self.coordinates):
            part_image = self.head['right'] if index == 0 else self.tail['right'] if index == self.body_size - 1 else self.body['right']
            self.images.append(canvas.create_image(x_axis, y_axis, image=part_image, anchor="nw", tag="snake"))

    def set_direction(self, new_direction):
        self.direction = new_direction

    def grow(self, x_axis, y_axis):
        self.coordinates.insert(0, (x_axis, y_axis))
        self.images.insert(0, self.canvas.create_image(x_axis, y_axis, image=self.head[self.direction], anchor="nw", tag="snake"))
        if len(self.images) > 1:
            self.canvas.itemconfig(self.images[1], image=self.body[self.direction])
        if len(self.images) >= 2:
            self._update_tail()

    def shrink(self):
        self.coordinates.pop()
        self.canvas.delete(self.images.pop())
        if len(self.coordinates) >= 2:
            self._update_tail()

    def _update_tail(self):
        second_to_last_x_axis, second_to_last_y_axis = self.coordinates[-2]
        last_x_axis, last_y_axis = self.coordinates[-1]
        if second_to_last_x_axis > last_x_axis:
            tail_direction = 'right'
        elif second_to_last_x_axis < last_x_axis:
            tail_direction = 'left'
        elif second_to_last_y_axis > last_y_axis:
            tail_direction = 'down'
        else:
            tail_direction = 'up'
        self.canvas.itemconfig(self.images[-1], image=self.tail[tail_direction])

class Food(GameObject):
    def __init__(self, canvas):
        x_axis = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y_axis = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        super().__init__(canvas, x_axis, y_axis)
        self.image = PhotoImage(file="assets/food.png")
        self.image_id = canvas.create_image(x_axis, y_axis, image=self.image, anchor="nw", tag="food")
        canvas.food_image = self.image

def next_turn():
    global score, direction, food
    delta_x_axis, delta_y_axis = {'up': (0, -SPACE_SIZE), 'down': (0, SPACE_SIZE), 'left': (-SPACE_SIZE, 0), 'right': (SPACE_SIZE, 0)}[direction]
    current_head_x_axis, current_head_y_axis = jake.coordinates[0]
    new_head_x_axis = current_head_x_axis + delta_x_axis
    new_head_y_axis = current_head_y_axis + delta_y_axis
    jake.grow(new_head_x_axis, new_head_y_axis)

    food_x_axis, food_y_axis = food.get_position()
    if (new_head_x_axis, new_head_y_axis) == (food_x_axis, food_y_axis):
        eat_sound.play()
        score += 1
        label.config(text=f"Score: {score}")
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
    if direction != {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}[new_direction]:
        direction = new_direction
        jake.set_direction(new_direction)

def check_collisions():
    head_x_axis, head_y_axis = jake.coordinates[0]
    return (
        head_x_axis < 0 or head_x_axis >= GAME_WIDTH or head_y_axis < 0 or head_y_axis >= GAME_HEIGHT or
        (head_x_axis, head_y_axis) in jake.coordinates[1:]
    )

def game_over():
    canvas.delete(ALL)
    canvas.game_over_background_image = PhotoImage(file="assets/jake_ending.png")
    canvas.create_image(0, 0, image=canvas.game_over_background_image, anchor="nw", tag="gameover_bg")
    canvas.create_text(GAME_WIDTH / 2, GAME_HEIGHT / 2, font=('consolas', 70), text="GAME OVER", fill="red", tag="gameover_text")
    pygame.mixer.music.stop()
    pygame.mixer.Sound("assets/jake_scream_sound.wav").play()
    pygame.mixer.music.load("assets/ending_bg_music.wav")
    pygame.mixer.music.play(-1)

window = Tk()
window.title("Jake's Sandwich Chase")
window.resizable(False, False)

score, direction = 0, 'down'
label = Label(window, text="Score: 0", font=('consolas', 40))
label.pack()
canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()
canvas.background_image = PhotoImage(file="assets/grass_bg.png")
canvas.create_image(0, 0, image=canvas.background_image, anchor="nw")

window.update()
window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + label.winfo_height()}+{int((window.winfo_screenwidth()/2) - (GAME_WIDTH/2))}+{int((window.winfo_screenheight()/2) - (GAME_HEIGHT/2))}")

for key, dir_key in {'<Left>': 'left', '<Right>': 'right', '<Up>': 'up', '<Down>': 'down'}.items():
    window.bind(key, lambda e, d=dir_key: change_direction(d))

jake = Jake(canvas)
food = Food(canvas)

pygame.mixer.init()
pygame.mixer.music.load("assets/adventure_time_bg_music.wav")
pygame.mixer.music.play(-1)
eat_sound = pygame.mixer.Sound("assets/eat_sound.wav")

next_turn()
window.mainloop()

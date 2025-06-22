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

class Snake(GameObject):
    def __init__(self, canvas):
        self.body_size = BODY_PARTS
        self.coordinates = [[0, 0] for _ in range(self.body_size)]
        self.images = []
        self.canvas = canvas

        self.current_direction = 'down'

        self.head_images = self.load_rotated_images("jake_head.png")
        self.body_images = self.load_rotated_images("jake_body.png")
        self.tail_images = self.load_rotated_images("jake_bottom.png")

        for i, (x_axis, y_axis) in enumerate(self.coordinates):
            if i == 0:
                image_id = canvas.create_image(x_axis, y_axis, image=self.head_images['right'], anchor="nw", tag="snake")
            elif i == self.body_size - 1:
                image_id = canvas.create_image(x_axis, y_axis, image=self.tail_images['right'], anchor="nw", tag="snake")
            else:
                image_id = canvas.create_image(x_axis, y_axis, image=self.body_images['right'], anchor="nw", tag="snake")
            self.images.append(image_id)


    def load_rotated_images(self, filename):
        base_image = Image.open(filename).resize((SPACE_SIZE, SPACE_SIZE))
        return {
            "up": ImageTk.PhotoImage(base_image),
            "down": ImageTk.PhotoImage(base_image.rotate(180)),
            "left": ImageTk.PhotoImage(base_image.rotate(90)),
            "right": ImageTk.PhotoImage(base_image.rotate(-90))
        }

    def set_direction(self, new_direction):
        self.current_direction = new_direction

    def grow(self, x_axis, y_axis):
        self.coordinates.insert(0, (x_axis, y_axis))
        image = self.head_images[self.current_direction]
        image_id = self.canvas.create_image(x_axis, y_axis, image=image, anchor="nw", tag="snake")
        self.images.insert(0, image_id)

        if len(self.images) > 1:
            old_head_id = self.images[1]
            self.canvas.itemconfig(old_head_id, image=self.body_images[self.current_direction])

        if len(self.images) >= 2:
            tail_id = self.images[-1]
            self.canvas.itemconfig(tail_id, image=self.tail_images[self.current_direction])


    def shrink(self):
        self.coordinates.pop()
        self.canvas.delete(self.images[-1])
        self.images.pop()

        if len(self.coordinates) >= 2:
            x1, y1 = self.coordinates[-2]
            x2, y2 = self.coordinates[-1]

            if x1 > x2:
                tail_dir = 'right'
            elif x1 < x2:
                tail_dir = 'left'
            elif y1 > y2:
                tail_dir = 'down'
            else:
                tail_dir = 'up'


            tail_id = self.images[-1]
            self.canvas.itemconfig(tail_id, image=self.tail_images[tail_dir])


class Food(GameObject):
    def __init__(self, canvas):
        x_axis = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y_axis = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        super().__init__(canvas, x_axis, y_axis)

        self.image = PhotoImage(file="food.png")
        self.image_id = canvas.create_image(x_axis, y_axis, image=self.image, anchor="nw", tag = "food")
        canvas.food_image = self.image

def next_turn():
    global score, direction, food

    x_axis, y_axis = snake.coordinates[0]

    if direction == "up":
        y_axis -= SPACE_SIZE
    elif direction == "down":
        y_axis += SPACE_SIZE
    elif direction == "left":
        x_axis -= SPACE_SIZE
    elif direction == "right":
        x_axis += SPACE_SIZE

    snake.grow(x_axis, y_axis)

    food_x, food_y = food.get_position()

    if x_axis == food_x and y_axis == food_y:
        eat_sound.play()
        score += 1
        label.config(text="Score:{}".format(score))
        canvas.delete("food")
        food = Food(canvas)
    else:
        snake.shrink()

    if check_collisions():
        game_over()
    else:
        window.after(SPEED, next_turn)

def change_direction(new_direction):
    global direction
    opposites = {'up': 'down', 'down': 'up', 'left': 'right', 'right': 'left'}
    if direction != opposites.get(new_direction):
        direction = new_direction
        snake.set_direction(new_direction)

def check_collisions():
    x, y = snake.coordinates[0]

    if x < 0 or x >= GAME_WIDTH or y < 0 or y >= GAME_HEIGHT:
        return True

    if (x, y) in snake.coordinates[1:]:
        return True

    return False

def game_over():
    canvas.delete(ALL)
    canvas.create_text(canvas.winfo_width() / 2, canvas.winfo_height() / 2,
                       font=('consolas', 70), text="GAME OVER", fill="red", tag="gameover")

window = Tk()
window.title("Snake Game")
window.resizable(False, False)

score = 0
direction = 'down'

label = Label(window, text="Score:{}".format(score), font=('consolas', 40))
label.pack()

canvas = Canvas(window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
canvas.pack()

#GRASS WALLPAPER
background_image = PhotoImage(file="grass_bg.png")
canvas.create_image(0, 0, image=background_image, anchor="nw")
canvas.background = background_image

window.update()
x = int((window.winfo_screenwidth() / 2) - (window.winfo_width() / 2))
y = int((window.winfo_screenheight() / 2) - (window.winfo_height() / 2))
window.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT + label.winfo_height()}+{x}+{y}")

window.bind('<Left>', lambda event: change_direction('left'))
window.bind('<Right>', lambda event: change_direction('right'))
window.bind('<Up>', lambda event: change_direction('up'))
window.bind('<Down>', lambda event: change_direction('down'))

snake = Snake(canvas)
food = Food(canvas)

pygame.mixer.init()
pygame.mixer.music.load(r"C:\Users\ACER\Desktop\final_project\adventure_time_bg_music.wav")
pygame.mixer.music.play(-1)

eat_sound = pygame.mixer.Sound("eat_sound.wav")

next_turn()
window.mainloop()

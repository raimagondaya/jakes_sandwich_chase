from tkinter import *
import random
import pygame

GAME_WIDTH = 800
GAME_HEIGHT = 600
SPEED = 150
SPACE_SIZE = 50
BODY_PARTS = 3
SNAKE_COLOR = "#00FF00"
FOOD_COLOR = "#FF0000"
BACKGROUND_COLOR = "#000000"

class GameObject:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.coordinates = [x, y]

class Snake(GameObject):
    def __init__(self, canvas):
        self.body_size = BODY_PARTS
        self.coordinates = [[0, 0] for _ in range(self.body_size)]
        self.squares = []
        self.canvas = canvas

        for x_axis, y_axis in self.coordinates:
            square = canvas.create_rectangle(x_axis, y_axis, x_axis + SPACE_SIZE, y_axis + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

    def grow(self, x_axis, y_axis):
        self.coordinates.insert(0, (x_axis, y_axis))
        square = self.canvas.create_rectangle(x_axis, y_axis, x_axis + SPACE_SIZE, y_axis + SPACE_SIZE, fill=SNAKE_COLOR)
        self.squares.insert(0, square)

    def shrink(self):
        del self.coordinates[-1]
        self.canvas.delete(self.squares[-1])
        del self.squares[-1]

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

    if x_axis == food.coordinates[0] and y_axis == food.coordinates[1]:
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

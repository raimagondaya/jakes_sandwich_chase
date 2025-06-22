from tkinter import *
import random
import pygame

GAME_WIDTH = 700
GAME_HEIGHT = 700
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

        for x, y in self.coordinates:
            square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
            self.squares.append(square)

    def grow(self, x, y):
        self.coordinates.insert(0, (x, y))
        square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR)
        self.squares.insert(0, square)

    def shrink(self):
        del self.coordinates[-1]
        self.canvas.delete(self.squares[-1])
        del self.squares[-1]

class Food(GameObject):
    def __init__(self, canvas):
        x = random.randint(0, (GAME_WIDTH // SPACE_SIZE) - 1) * SPACE_SIZE
        y = random.randint(0, (GAME_HEIGHT // SPACE_SIZE) - 1) * SPACE_SIZE
        super().__init__(canvas, x, y)
        self.canvas.create_oval(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")

def next_turn():
    global score, direction, food

    x, y = snake.coordinates[0]

    if direction == "up":
        y -= SPACE_SIZE
    elif direction == "down":
        y += SPACE_SIZE
    elif direction == "left":
        x -= SPACE_SIZE
    elif direction == "right":
        x += SPACE_SIZE

    snake.grow(x, y)

    if x == food.coordinates[0] and y == food.coordinates[1]:
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

window.update()
x = int((window.winfo_screenwidth() / 2) - (window.winfo_width() / 2))
y = int((window.winfo_screenheight() / 2) - (window.winfo_height() / 2))
window.geometry(f"{window.winfo_width()}x{window.winfo_height()}+{x}+{y}")

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

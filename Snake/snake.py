import turtle
import snake_class
from food import Food
from scoreboard import Scoreboard
import time

######################################################
screen = turtle.Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("Snakealiscious")
# Turning the tracer off.
screen.tracer(0)
# Creating a snake object from the Snake class / blueprint
snake = snake_class.Snake()
# Creating a food object from the Food class
food = Food()
# Start listening for key strokes Up arrow, Down arrow, Left arrow and Right arrow
scoreboard = Scoreboard()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")
######################################################

game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.1)
    # Every time the screen refreshes, move the snake forward by one step
    snake.move()
    # Detect collision with food using the distance() method within the turtle library
    if snake.head.distance(food) < 15:
        food.refresh()
        scoreboard.increase_score()
        snake.extend()

    # Detect collision with wall
    if snake.head.xcor() > 290 or snake.head.xcor() < -290 or snake.head.ycor() > 290 or snake.head.ycor() < -290:
        game_is_on = False
        scoreboard.game_over()

    # Detect collision with tail
    # Slice the list of segments so that you return everything except the first item
    for i in snake.segments[1:]:
        if snake.head.distance(i) < 10:
            game_is_on = False
            scoreboard.game_over()

screen.exitonclick()
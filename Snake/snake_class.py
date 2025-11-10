import turtle

# Setting the standard unchanging variables of the game
STARTING_POSITIONS = [(0, 0), (-20, 0), (-40, 0)]
MOVE_DISTANCE = 20
UP = 90
DOWN = 270
LEFT = 180
RIGHT = 0

class Snake:
    def __init__(self):
        self.segments = []
        self.create_snake()
        self.head = self.segments[0]
    
    def create_snake(self):
        for i in STARTING_POSITIONS:
            self.add_segment(i)

    def add_segment(self, position):
        new_segment =  turtle.Turtle(shape="square")
        new_segment.color("white")
        new_segment.penup()
        new_segment.goto(position)
        self.segments.append(new_segment)
    
    def extend(self):
        # Add the new segment to the position of the last segment
        self.add_segment(self.segments[-1].position())
    
    def move(self):
        for i in range(len(self.segments) - 1, 0, -1):
            # Getting the x and y coordinates of the second to last segment in the 'segments' list
            new_x = self.segments[i - 1].xcor()
            new_y = self.segments[i - 1].ycor()
             # Telling the last segment to go to the coordinates of the second to last segment
            self.segments[i].goto(x=new_x, y=new_y)
        # Getting the segment at the front of the snake to move forwards 20 pixels
        self.head.forward(MOVE_DISTANCE)

    def up(self):
        if self.head.heading() != DOWN:
            self.head.setheading(UP)

    def down(self):
        if self.head.heading() != UP:
            self.head.setheading(DOWN)

    def left(self):
        if self.head.heading() != RIGHT:
            self.head.setheading(LEFT)

    def right(self):
        if self.head.heading() != LEFT:
            self.head.setheading(RIGHT)
from turtle import Turtle


class Scoreboard(Turtle):

    def __init__(self):
        super().__init__()
        self.score = 0
        self.penup()
        self.hideturtle()
        self.color("White")
        self.goto(0, 250)
        self.write(f"Score = {self.score}", False, align="center", font=("Arial", 18, "normal"))


    def addscore(self):
        self.clear()
        self.score += 1
        self.write(f"Score = {self.score}", False, align="center", font=("Arial", 18, "normal"))

    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", False, align="center", font=("Arial", 18, "normal"))
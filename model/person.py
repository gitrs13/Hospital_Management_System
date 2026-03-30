class Person:
    """Base class — shared attributes for Doctor and Patient."""

    def __init__(self, name: str, age: int, gender: str):
        self.name   = name
        self.age    = age
        self.gender = gender

    def show_details(self):
        print(f"Name   : {self.name}")
        print(f"Age    : {self.age}")
        print(f"Gender : {self.gender}")

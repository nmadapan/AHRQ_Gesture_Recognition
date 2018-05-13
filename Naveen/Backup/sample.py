import sys, os

class Dog:

    __name = 'canine'         # class variable shared by all instances

    def __init__(self, name):
        self.name = name    # instance variable unique to each instance

a = Dog('Hello')
b = Dog('World')

print _Dog__name
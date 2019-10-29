from __future__ import unicode_literals
from django.db import models
from django.contrib import messages


class UserManager(models.Manager):

    def basic_validator(self, postData):
        errors = {}
        # add keys and values to errors dictionary for each invalid field
        if len(postData["firstName"]) < 2:
            errors["firstName"] = "User First Name should be at least 2 characters"
        if len(postData["lastName"]) < 2:
            errors["lastName"] = "User Last Name Should be Longer than that"
        if len(postData["email"]) < 2:
            errors["email"] = "email must be a valid email"
        if len(postData["username"]) < 5:
            errors["username"] = "Username must be at least 5 characters long"
        if len(postData["password"]) < 8:
            errors["password"] = "Password must be at least 8 character long"
        if postData["password"] != postData['confirm']:
            errors["password"] = "Password does not match. Try again"

        return errors

    def login_validator(self, postData):
        errors = {}
        if len(postData["username"]) < 1:
            errors["username"] = "Email cannot be blank"
        if len(postData["password"]) < 1:
            errors["password"] = "Password cannot be blank"

        return errors
        


class User(models.Model):
    firstName   = models.CharField(max_length=255)
    lastName    = models.CharField(max_length=255)
    username    = models.CharField(max_length=255)
    email       = models.EmailField(max_length=255)
    password    = models.CharField(max_length=255)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    objects     = UserManager()

    def __repr__(self):
        return f" ID: {self.id}, Name: {self.firstName} {self.lastName}, Email: {self.email}, Username: {self.username}, Password: {self.password}"

class Message(models.Model):
    message     = models.CharField(max_length=255, null=True)
    user        = models.ForeignKey(User, related_name="messages", null=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    objects     = UserManager()

    def __repr__(self):
        return f" ID: {self.id}, Message: {self.message}"

class Comment(models.Model):
    comment     = models.CharField(max_length=255, null=True)
    message     = models.ForeignKey(Message, related_name="comments")
    user        = models.ForeignKey(User, related_name="comments")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    objects     = UserManager()

    def __repr__(self):
        return f" ID: {self.id}, Comment: {self.comment}"




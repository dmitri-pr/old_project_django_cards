from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.models import User
from django.conf import settings
from taggit.managers import TaggableManager


class Word(models.Model):
    writing = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1, "Word must be greater than 1 characters")]
    )
    old_writing = models.CharField(max_length=200)
    transcription = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meanings = models.ManyToManyField('Meaning', through='CrossTable')
    tags = TaggableManager(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("writing", "owner")

    def __str__(self):
        return self.writing


class Meaning(models.Model):
    text = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1, "Meaning must be greater than 1 characters")]
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("text", "owner")

    def __str__(self):
        return self.text


class CrossTable(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE)
    username = models.CharField(max_length=200, default=None)

    class Meta:
        unique_together = ("word", "meaning", "username")


class Comment(models.Model):
    text = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )

    word_meaning = models.ForeignKey(CrossTable, on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("text", "word_meaning", "owner")

    def __str__(self):
        if len(self.text) < 15:
            return self.text
        return self.text[:11] + ' ...'


class Tag(models.Model):
    text = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(1, "Tag must be greater than 1 characters")]
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("text", "owner")

    def __str__(self):
        return self.text

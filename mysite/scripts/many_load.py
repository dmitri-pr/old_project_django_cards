import csv  # https://docs.python.org/3/library/csv.html

# https://django-extensions.readthedocs.io/en/latest/runscript.html

# python3 manage.py runscript many_load
import re
from cards.models import Word, Meaning, CrossTable, Comment, Tag
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


def run():
    fhand = open('cards/MY_.csv', encoding="utf-8")
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    owner = User.objects.get(username='user')

    Word.objects.filter(owner=owner).delete()
    Meaning.objects.filter(owner=owner).delete()
    CrossTable.objects.filter(username=owner.username).delete()
    Comment.objects.filter(owner=owner).delete()
    Tag.objects.filter(owner=owner).delete()

    tag, created = Tag.objects.get_or_create(text='0', owner=owner)

    for row in reader:

        row = row[0].split(",")
        if row[0] == '"': continue
        writing = row[1].replace('"', '').strip()
        old_writing = row[2].replace('"', '').strip()
        transcr = row[3].replace('"', '').strip()
        meanings = ','.join(row[4:]).replace('"', '').replace(';', ',').replace('1)', '').replace(' 2)', ',').replace(
            ' 3)', ',').replace(' 4)', ',').replace(' 5)', ',').replace(' 6)', ',').replace(' 7)', ',').replace(
            ' 8)', ',').replace(' 9)', ',').replace(',,', ',').strip().split(',')

        try:
            word, created = Word.objects.get_or_create(writing=writing, old_writing=old_writing, transcription=transcr,
                                                       owner=owner)
        except:
            word = Word.objects.get(writing=writing, owner=owner)
            word.transcription = transcr + ' ' + '/' + ' ' + word.transcription

        if not word.tags.all() or '0' not in word.tags.all():
            word.tags.add('0')
            word.save()
        print(word)

        for meaning in meanings:
            meaning_clean = meaning.strip()
            comments = ''
            if re.findall(r'\([^(]+\)', meaning):
                meaning_clean = re.sub(r'\([^(]+\)', '', meaning).strip()
                comments = re.findall(r'\([^(]+\)', meaning)
                print(comments)

            mean, created = Meaning.objects.get_or_create(text=meaning_clean, owner=owner)
            print(mean)
            ct, created = CrossTable.objects.get_or_create(word=word, meaning=mean, username=owner.username)
            print(word)

            if comments:
                for comment in comments:
                    comment = comment.replace('(', '').replace(')', '').strip()
                    word_meaning = ct
                    Comment.objects.get_or_create(text=comment, owner=owner, word_meaning=word_meaning)



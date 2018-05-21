from django.core.management.base import BaseCommand
from qSite.models import *
import random


class Command(BaseCommand):
  help = 'Seeds database with test data'

  USERS_COUNT = Profile.objects.count()
  QUESTIONS_COUNT = Question.objects.count()
  QUESTION_LIKES_PER_USER = 100
  ANSWERS_LIKES_PER_USER = 100


  def handle(self, *args, **options):
    users = Profile.objects.all()
    self.generate_likes_fast(users=users)
    self.stdout.write(self.style.SUCCESS('Successfully generated data.'))


  def generate_likes(self, users):
    Like.objects.all().delete()

    for user in users:
      list_of_likes = []

      questions = Question.objects.all().exclude(author=user)
      count = questions.count()
      slice = random.random() * (count - 1000)
      questions = questions[slice: slice + 1000]
      for question in questions:
        value = random.choice([1, -1])
        like = Like(value=value, author=user, content_object=question)
        list_of_likes.append(like)

      answers = Answer.objects.all().exclude(author=user)
      count = answers.count()
      slice = random.random() * (count - 1000)
      answers = answers[slice: slice + 1000]
      for answer in answers:
        value = random.choice([1, -1])
        like = Like(value=value, author=user, content_object=answer)
        list_of_likes.append(like)

      Like.objects.bulk_create(list_of_likes)
      for like in list_of_likes:
        like.content_object.update_rating()
      print('Created and saved bunch of likes.')
      print(user.pk)
      if Like.objects.count() > 2000000:
        break
    self.stdout.write(self.style.SUCCESS('Successfully generated likes.'))




  def generate_likes_fast(self, users):
    Like.objects.all().delete()

    questions = Question.objects.filter(pk__lte=10000)
    answers = Answer.objects.filter(pk__lte=10000)

    i = 1

    while(Like.objects.all().count() < 2000000):
        user = users[i]
        i += 1
        list_of_likes = []

        _questions = questions.exclude(author=user)
        for question in _questions:
          value = random.choice([1, -1])
          like = Like(value=value, author=user, content_object=question)
          list_of_likes.append(like)

        _answers = answers.exclude(author=user)
        for answer in _answers:
          value = random.choice([1, -1])
          like = Like(value=value, author=user, content_object=answer)
          list_of_likes.append(like)

        Like.objects.bulk_create(list_of_likes)
        for like in list_of_likes:
          like.content_object.rating += like.value
          like.content_object.save(update_fields=['rating'])
    self.stdout.write(self.style.SUCCESS('Successfully generated likes.'))
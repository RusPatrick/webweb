from django.core.management.base import BaseCommand
from qSite.models import *
from faker import Faker
import random
from pytz import timezone
from itertools import islice


class Command(BaseCommand):
  help = 'Seeds database with test data'

  USERS_COUNT = 10000
  TAGS_COUNT = 10000
  MAX_QUESTIONS_PER_USER = 15
  MAX_ANSWERS_PER_QUESTION = 15


  def handle(self, *args, **options):
    users = self.generate_users()
    tags = self.generate_tags()
    questions = self.generate_questions(users=users, tags=tags)
    self.generate_answers(questions=questions, users=users)
    self.stdout.write(self.style.SUCCESS('Successfully generated data.'))


  def generate_users(self):
    Profile.objects.all().delete()
    list_of_users = []

    fake = Faker()
    for i in range(0, self.USERS_COUNT):
      username = fake.simple_profile().get("username") + str(i)
      user = Profile(username=username)
      user.set_password(username)
      user.first_name = fake.first_name()
      user.last_name = fake.last_name()
      user.rating = random.randint(-50, 50)
      list_of_users.append(user)

    Profile.objects.bulk_create(list_of_users)

    self.stdout.write(self.style.SUCCESS('Successfully generated users.'))
    return Profile.objects.all()


  def generate_tags(self):
    Tag.objects.all().delete()
    list_of_tags = []

    fake = Faker()
    for i in range(0, self.TAGS_COUNT):
      name = fake.word()[:9] + str(i)
      tag = Tag(name=name)
      list_of_tags.append(tag)

    Tag.objects.bulk_create(list_of_tags)

    self.stdout.write(self.style.SUCCESS('Successfully generated tags.'))
    return Tag.objects.all()


  def generate_questions(self, users, tags):
    Question.objects.all().delete()

    fake = Faker()
    for user in users:
      for i in range(0, random.randint(10, self.MAX_QUESTIONS_PER_USER)):
        title = fake.sentence(nb_words=8)[:98]
        text = fake.text()
        creationTime = fake.date_time_this_year(
          before_now=True,
          after_now=False,
          tzinfo=timezone('Europe/Moscow')
        )
        author = user
        question = Question(
          title=title,
          text=text,
          creationTime=creationTime,
          author=author
        )
        question.save()
        tags_to_add = []
        for i in range(0, 3):
          tags_to_add.append(random.choice(tags).pk)
        question.tags.add(*tags_to_add)

    self.stdout.write(self.style.SUCCESS('Successfully generated questions.'))
    return Question.objects.all()


  def generate_answers(self, questions, users):
    Answer.objects.all().delete()
    list_of_answers = []

    fake = Faker()
    for question in questions:
      for i in range(0, random.randint(10, self.MAX_ANSWERS_PER_QUESTION)):
        user = random.choice(users)
        text = fake.text()
        creationTime = fake.date_time_this_year(
          before_now=True,
          after_now=False,
          tzinfo=timezone('Europe/Moscow')
        )
        answer = Answer(
          text=text,
          creationTime=creationTime,
          author=user,
          question=question
        )
        list_of_answers.append(answer)

    batch_size = 10000
    start = 0
    end = 10000
    while True:
      batch = list(islice(list_of_answers, start, end))
      if not batch:
        break
      Answer.objects.bulk_create(batch)
      start = start + batch_size
      end = end + batch_size

    self.stdout.write(self.style.SUCCESS('Successfully generated answers.'))
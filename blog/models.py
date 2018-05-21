from django.db import models
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import UserManager as AbstractUserManager
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.dispatch import receiver

# from django.db.models import Q

class UserManager(AbstractUserManager):

  def by_username(self, _username):
    return self.get(username=_username)
    # return get_object_or_404(self, username=_username)

  def by_id(self, _id):
    return get_object_or_404(self, pk=_id)

  def by_rating(self):
    return self.order_by('-rating')

  def search(self, _q):
    return self.filter(username__icontains=_q).order_by('-rating')


class TagManager(models.Manager):

  def by_tag_newest(self, _tag):
    return get_object_or_404(self, name=_tag).questions.all().order_by('-creationTime')

  def hottest(self):
    return self.annotate(question_count=Count('questions')).order_by('-question_count')

  def search(self, _q):
    return self.hottest().filter(name__icontains=_q)

class LikeManager(models.Manager):
  pass


class QuestionManager(models.Manager):

  def newest(self):
    return self.all()

  def hottest(self):
    return self.order_by('-rating')

  def by_id(self, _id):
    return get_object_or_404(self, pk=_id)

  def search(self, _q):
    return self.filter(tags__name__icontains=_q).order_by('-rating')
    # return self.filter(Q(title__icontains=q) | Q(text__icontains=q))


class AnswerManager(models.Manager):

  def hottest(self, qid):
    return self.filter(question__id=qid).order_by('-rating', '-creationTime')


class Like(models.Model):
  LIKE = 1
  DISLIKE = -1
  VALUES = ((DISLIKE, 'DISLIKE'), (LIKE, 'LIKE'),)
  author = models.ForeignKey(
    'Profile',
    null=False,
    verbose_name="Author of the vote",
    on_delete=models.CASCADE
  )
  value = models.IntegerField(
    choices=VALUES,
    verbose_name="Like or dislike",
    null=False
  )

  content_type = models.ForeignKey(
    ContentType,
    on_delete=models.CASCADE,
    null=True
  )
  object_id = models.PositiveIntegerField(
    null=True,
    verbose_name="id of related object"
  )
  content_object = GenericForeignKey('content_type', 'object_id')

  objects = LikeManager()

  def __str__(self):
    return str(self.value) + ' from ' + self.author.username

  class Meta:
    unique_together = ('author', 'content_type', 'object_id',)


class Profile(AbstractUser):
  avatar = models.ImageField(
    blank=False,
    default="nobody.jpg",
    upload_to='uploads/%Y/%m/%d/',
    verbose_name="Avatar image of the user"
  )

  likes = GenericRelation(Like, related_query_name='profiles')
  rating = models.IntegerField(default=0, verbose_name="Rating of the user")

  objects = UserManager()
  # AbstractUser._meta.get_field('email')._unique = True
  def get_questions(self):
    return self.questions.order_by('-creationTime')

  def get_answers(self):
    return self.answers.order_by('-creationTime')

  def is_liked_by(self, user):
    like_ = self.likes.filter(author=user)
    if not like_.exists():
      return 0
    else:
      return like_.first().value

  def update_rating(self):
    self.rating = self.likes.aggregate(Sum('value')).get('value__sum')
    self.save(update_fields=['rating'])

  def __str__(self):
    return self.username

  class Meta:
    ordering = ['-rating']


class Tag(models.Model):
  name = models.CharField(max_length=15, verbose_name="Name of the tag")

  objects = TagManager()

  def __str__(self):
    return self.name

  class Meta:
    ordering = ['name']


class Question(models.Model):
  author = models.ForeignKey(
    Profile,
    null=False,
    verbose_name="Author of the question",
    on_delete=models.CASCADE,
    related_name='questions'
  )

  title = models.CharField(
    max_length=100,
    verbose_name="Title of the question"
  )
  text = models.TextField(verbose_name="Full text of the question")
  tags = models.ManyToManyField(
    Tag,
    blank=True,
    verbose_name="Tags of the question",
    related_name='questions'
  )
  creationTime = models.DateTimeField(
    default=timezone.now,
    verbose_name="Date and time the question was published"
  )

  likes = GenericRelation(Like, related_query_name='questions')
  rating = models.IntegerField(default=0, verbose_name="Votes ratio")

  objects = QuestionManager()

  def is_answered_by(self, user):
    return self.answer_set.filter(author=user).exists()

  def update_rating(self):
    self.rating = self.likes.aggregate(Sum('value')).get('value__sum')
    self.save(update_fields=['rating'])

  def is_liked_by(self, user):
    like_ = self.likes.filter(author=user)
    if not like_.exists():
      return 0
    else:
      return like_.first().value

  def __str__(self):
    return self.text

  class Meta:
    ordering = ['-creationTime']


class Answer(models.Model):
  author = models.ForeignKey(
    Profile,
    null=False,
    verbose_name="Author of the answer",
    on_delete=models.CASCADE,
    related_name='answers'
  )
  question = models.ForeignKey(
    Question,
    null=False,
    on_delete=models.CASCADE,
    verbose_name="Question that is being answered"
  )

  text = models.TextField(verbose_name="Full text of the answer")
  creationTime = models.DateTimeField(
    default=timezone.now,
    verbose_name="Date and time the answer was published"
  )

  likes = GenericRelation(Like, related_query_name='answers')
  rating = models.IntegerField(default=0, verbose_name="Votes ratio")
  is_correct = models.BooleanField(
    default=False,
    verbose_name="If answer is marked as correct"
  )

  objects = AnswerManager()

  def get_page(self):
    return int(Answer.objects.hottest(self.question.id).filter(rating__gte=self.rating).filter(creationTime__lte=self.creationTime).count() / 30) + 1

  def update_rating(self):
    self.rating = self.likes.aggregate(Sum('value')).get('value__sum')
    self.save(update_fields=['rating'])

  def is_liked_by(self, user):
    like_ = self.likes.filter(author=user)
    if not like_.exists():
      return 0
    else:
      return like_.first().value

  def __str__(self):
    return self.text

  class Meta:
    ordering = ['-creationTime']

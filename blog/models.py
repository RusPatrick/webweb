from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, UserManager


class QuestionManager(models.Manager):
    def sortByDate(self):
        objects_list = []
        questions = self.order_by('-date')
        for question in questions:
            list_element = question
            list_element.answers_count = Answer.objects.filter(question_id=question.id).count()
            objects_list.append(list_element)
        return objects_list

    def bestQuestions(self):
        objects_list = []
        questions = self.order_by('-ratin')
        for question in questions:
            list_element = question
            list_element.answers_count = Answer.objects.filter(question_id=question.id).count()
            objects_list.append(list_element)
        return objects_list

    def questionsByTag(self, tag):
        return Question.objects.filter(tags__text=tag)


class UserM(UserManager):
    def bestUsers(self):
        return User.objects.annotate(total=Count('author')).order_by("-total")[:5]


class AnswerManager(models.Manager):
    def answersOnQuestion(self, id):
        return Answer.objects.filter(question_id=id)


class TagManager(models.Manager):
    def bestTags(self):
        return Tag.objects.annotate(total=Count('tags')).order_by("-total")[:5]


class User(AbstractUser):
    avatar = models.ImageField(upload_to='user_pics/%Y/%m/%d/', default='user_pics/man.svg')
    nick = models.CharField(max_length=20)
    objects = UserM()


class Tag(models.Model):
    text = models.CharField(max_length=200)
    objects = TagManager()

    def __unicode__(self):
        return self.text


class Question(models.Model):
    asking = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author")
    title = models.CharField(max_length=200)
    text = models.TextField()
    ratin = models.IntegerField()
    tags = models.ManyToManyField(Tag, related_name="tags")
    date = models.DateTimeField(default=timezone.now)
    objects = QuestionManager()


class Answer(models.Model):
    answerer = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(max_length=200)  # найти тип данных побольше!
    correct = models.BooleanField()
    date = models.DateTimeField(default=timezone.now)
    objects = AnswerManager()

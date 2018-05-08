from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractUser, UserManager



class UserManager(UserManager):
    def by_username(self, _username):
        return get_object_or_404(self, username=_username)

    def by_id(self, _id):
        return get_object_or_404(self, pk=_id)

    def by_rating(self):
        return self.order_by('-rating')

    def search(self, _q):
        return self.filter(username__icontains=_q).order_by('-rating')


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

class LikeManager(models.Manager):
    pass


class TagManager(models.Manager):
    def by_tag_newest(self, _tag):
        return get_object_or_404(self, name=_tag).questions.all().order_by('-creationTime')

    def hottest(self):
        return self.annotate(question_count=Count('questions')).order_by('-question_count')

    def search(self, _q):
        return self.hottest().filter(name__icontains=_q)


class Profile(AbstractUser):
    avatar = models.ImageField(
        blank=False,
        default="user_pics/boss-1.png",
        upload_to='uploads/%Y/%m/%d',
        verbose_name="Avatar image of the user"
    )
    rating = models.IntegerField(default=0, verbose_name="Rating of the user")
    objects = UserManager()

    def get_objects(self):
        return self.questions.order_by('-creationTime')

    def get_answer(self):
        return self.answers.order_by('-creationTime')

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


class Like(models.Model):
    LIKE = 1
    DISLIKE = -1
    VALUES = ((DISLIKE, 'DISLIKE'), (LIKE, 'LIKE'))
    author = models.ForeignKey (
        Profile,
        null = False,
        verbose_name = "Author of the like",
        on_delete = models.CASCADE
    )

    value = models.IntegerField (
        choices = VALUES,
        verbose_name = "Like or dislike",
        null = False
    )

    content_type = models.ForeignKey (
        ContentType,
        on_delete = models.CASCADE,
        null = True
    )

    object_id = models.PositiveIntegerField (
        null = True,
        verbose_name = "if of related object"
    )

    content_object = GenericForeignKey ('content_type', 'object_id')

    objects = LikeManager()

    def __str__(self):
        return str(self.value) + 'from' + self.author.username

    class Meta:
        unique_together = ('author', 'content_type', 'object_id')


class Question(models.Model):
    author = models.ForeignKey(
        Profile,
        null = False,
        verbose_name = "Author of the Quetstion",
        on_delete = models.CASCADE,
        related_name = 'questions'
    )

    title = models.CharField ( max_length = 120, verbose_name = "Title of the question")
    text = models.TextField ()
    tags = models.ManyToManyField (
        Tag,
        blank = True,
        verbose_name = "tags of the Question",
        related_name = 'questions'
    )
    creationTime = models.DateTimeField (
        default = timezone.now,
        verbose_name = "Creation date of the question"
    )
    likes = GenericRelation(Like, related_query_name = "questions")
    rating = models.IntegerField(default=0, verbose_name="Votes ratio")

    objects = QuestionManager()

    def is_answered_by(self, user):
        return self.answer_set.filter(author=user).exists()

    def update_rating(self):
        # print('Update_rating fired!')
        like_count = self.likes.filter(value=1).count()
        dislike_count = self.likes.filter(value=-1).count()
        self.rating = like_count - dislike_count
        self.save(update_fields=['rating'])

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
        # print('Update_rating fired!')
        like_count = self.likes.filter(value=1).count()
        dislike_count = self.likes.filter(value=-1).count()
        self.rating = like_count - dislike_count
        self.save(update_fields=['rating'])

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-creationTime']
        # unique_together = ('author', 'question')

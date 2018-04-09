from django.core.management.base import BaseCommand, CommandError
from .models import Question

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('qid', nargs='+', type=int)

    def handle(self, *args, **options):
        for qid in options['qid']:
            try:
                question = Question.objects.get(pk=qid)
            except Question.DoesNotExist:
                raise CommandError('Quiestion "%s" does not exist' % qid)

            question.opened = False
            question.save()

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s"' % qid))

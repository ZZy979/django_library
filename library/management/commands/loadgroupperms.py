from django.contrib.auth.models import Group, Permission
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Load library user groups and permissions'

    def handle(self, *args, **options):
        # create groups
        librarian_group, _ = Group.objects.get_or_create(name='Librarian')
        self.stdout.write('Created Librarian group')

        # add permissions
        perm_names = [
            'add_book', 'change_book', 'delete_book', 'view_book',
            'add_category', 'change_category', 'delete_category', 'view_category',
            'view_borrowrecord'
        ]
        librarian_perms = Permission.objects.filter(codename__in=perm_names)
        librarian_group.permissions.set(librarian_perms)
        self.stdout.write('Set Librarian group permissions to {}'.format(librarian_perms))

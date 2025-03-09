from urllib.parse import quote

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import User, Book, BorrowRecord


class UserRegisterTest(TestCase):

    def setUp(self):
        self.data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123'
        }

    def test_success(self):
        response = self.client.post(reverse('library:register'), self.data)
        self.assertRedirects(response, reverse('library:login'))
        self.assertTrue(self.client.login(username='testuser', password='testpassword123'))
        user = User.objects.get(username='testuser')
        self.assertEqual('testuser@example.com', user.email)

        response = self.client.post(reverse('library:register'), self.data)
        self.assertTemplateUsed(response, 'library/register.html')
        self.assertContains(response, 'A user with that username already exists.')

    def test_passwords_not_match(self):
        self.data['password2'] = 'testpassword456'
        response = self.client.post(reverse('library:register'), self.data)
        self.assertTemplateUsed(response, 'library/register.html')
        self.assertFalse(User.objects.filter(username='testuser').exists())
        self.assertContains(response, 'The two password fields didn’t match.')

    def test_invalid_username(self):
        self.data['username'] = '#$%'
        response = self.client.post(reverse('library:register'), self.data)
        self.assertTemplateUsed(response, 'library/register.html')
        self.assertContains(response, 'Enter a valid username.')


def create_test_users():
    call_command('loadgroupperms')
    User.objects.create_user(username='testuser', password='testpassword123')
    User.objects.create_user(username='testuser2', password='testpassword456')
    admin_user = User.objects.create_user(username='testadmin', password='testpassword789')
    admin_user.groups.add(Group.objects.get(name='Librarian'))


class UserLoginTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_users()

    def test_success(self):
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(reverse('library:login'), data)
        self.assertRedirects(response, reverse('library:book-list'))

    def test_fail(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('library:login'), data)
        self.assertTemplateUsed(response, 'library/login.html')
        self.assertContains(response, 'Invalid username or password.')


class UserProfileTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_users()

    def setUp(self):
        self.client.login(username='testuser', password='testpassword123')

    def test_get(self):
        response = self.client.get(reverse('library:profile'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'library/user_profile.html')

    def test_success(self):
        data = {'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice@example.com'}
        response = self.client.post(reverse('library:profile'), data)
        self.assertRedirects(response, reverse('library:book-list'))
        user = User.objects.get(username='testuser')
        self.assertEqual('Alice', user.first_name)
        self.assertEqual('Smith', user.last_name)
        self.assertEqual('alice@example.com', user.email)

    def test_invalid_email(self):
        data = {'first_name': 'Alice', 'last_name': 'Smith', 'email': 'invalid_email'}
        response = self.client.post(reverse('library:profile'), data)
        self.assertTemplateUsed(response, 'library/user_profile.html')
        self.assertContains(response, 'Enter a valid email address.')

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('library:profile')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(url))


class SearchBookViewTest(TestCase):
    fixtures = ['books.json']

    @classmethod
    def setUpTestData(cls):
        cls.django = Book.objects.get(title='Django for Beginners')
        for i in range(25):
            Book.objects.create(title=f'Book {i}', author=f'Author {i}', isbn=str(i))

    def test_search_by_title(self):
        response = self.client.get(reverse('library:book-list'), {'title': 'django'})
        self.assertEqual(200, response.status_code)
        values = ['Django for Beginners']
        self.assertQuerySetEqual(response.context['book_list'], values, transform=lambda b: b.title)

    def test_search_by_category(self):
        response = self.client.get(reverse('library:book-list'), {'category': 1})
        self.assertEqual(200, response.status_code)
        values = ['Django for Beginners', 'Python Crash Course']
        self.assertQuerySetEqual(response.context['book_list'], values, transform=lambda b: b.title)

    def test_combined_search(self):
        response = self.client.get(reverse('library:book-list'), {'title': 'book', 'author': '8'})
        self.assertEqual(200, response.status_code)
        values = ['Book 8', 'Book 18']
        self.assertQuerySetEqual(response.context['book_list'], values, transform=lambda b: b.title)

    def test_search_no_results(self):
        response = self.client.get(reverse('library:book-list'), {'title': 'flask'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'No results found.')

    def test_pagination(self):
        response = self.client.get(reverse('library:book-list'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(20, len(response.context['book_list']))
        page_obj = response.context['page_obj']
        self.assertEqual(1, page_obj.number)
        self.assertEqual(2, page_obj.paginator.num_pages)

        response = self.client.get(reverse('library:book-list'), {'page': 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, len(response.context['book_list']))
        self.assertEqual(2, response.context['page_obj'].number)

    def test_pagination_with_search(self):
        response = self.client.get(reverse('library:book-list'), {'title': 'Book', 'page': 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.context['book_list']))
        self.assertIn('title=Book', response.context['querystring'])


class BookDetailViewTest(TestCase):
    fixtures = ['books.json']

    def test_book_detail(self):
        response = self.client.get(reverse('library:book-detail', args=(1,)))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'Django for Beginners')
        self.assertContains(response, 'William S. Vincent')
        self.assertContains(response, '9781735467269')
        self.assertContains(response, 'WelcomeToCode')
        self.assertContains(response, '2024-07-10')
        self.assertContains(response, 'Programming')
        self.assertContains(response, 'Django for Beginners is the fifth edition of the leading guide to '
                                      'building real-world web applications with Python.')

    def test_not_found(self):
        response = self.client.get(reverse('library:book-detail', args=(9999,)))
        self.assertEqual(404, response.status_code)


class BookCreateViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_users()

    def setUp(self):
        self.client.login(username='testadmin', password='testpassword789')

    def test_get(self):
        response = self.client.get(reverse('library:add-book'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'library/book_form.html')

    def test_post(self):
        data = {'title': 'Test Book', 'author': 'Test Author', 'isbn': '9781234567890', 'quantity': 1}
        response = self.client.post(reverse('library:add-book'), data)
        self.assertRedirects(response, reverse('library:book-list'))
        self.assertTrue(Book.objects.filter(title='Test Book').exists())

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('library:add-book')
        response = self.client.post(url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(url))

    def test_unauthorized(self):
        self.client.login(username='testuser', password='testpassword123')
        url = reverse('library:add-book')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        response = self.client.post(url)
        self.assertEqual(403, response.status_code)


class BookUpdateViewTest(TestCase):
    fixtures = ['books.json']

    @classmethod
    def setUpTestData(cls):
        create_test_users()

    def setUp(self):
        self.client.login(username='testadmin', password='testpassword789')

    def test_get(self):
        response = self.client.get(reverse('library:edit-book', args=(1,)))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'library/book_form.html')
        self.assertContains(response, 'Django for Beginners')

    def test_post(self):
        data = {
            'title': 'Django for Beginners (5th Edition)',
            'author': 'William S. Vincent',
            'isbn': '9781735467269',
            'quantity': 10
        }
        response = self.client.post(reverse('library:edit-book', args=(1,)), data)
        self.assertRedirects(response, reverse('library:book-list'))
        book = Book.objects.get(pk=1)
        self.assertEqual(data['title'], book.title)
        self.assertEqual(data['quantity'], book.quantity)

    def test_not_found(self):
        response = self.client.get(reverse('library:edit-book', args=(9999,)))
        self.assertEqual(404, response.status_code)

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('library:edit-book', args=(1,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(url))

    def test_unauthorized(self):
        self.client.login(username='testuser', password='testpassword123')
        url = reverse('library:edit-book', args=(1,))
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        response = self.client.post(url)
        self.assertEqual(403, response.status_code)


class BookDeleteViewTest(TestCase):
    fixtures = ['books.json']

    @classmethod
    def setUpTestData(cls):
        create_test_users()

    def setUp(self):
        self.client.login(username='testadmin', password='testpassword789')

    def test_get(self):
        response = self.client.get(reverse('library:delete-book', args=(2,)))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'library/book_confirm_delete.html')
        self.assertContains(response, 'Are you sure you want to delete "Python Crash Course"?')

    def test_post(self):
        response = self.client.post(reverse('library:delete-book', args=(2,)))
        self.assertRedirects(response, reverse('library:book-list'))
        self.assertFalse(Book.objects.filter(pk=2).exists())

    def test_not_found(self):
        response = self.client.get(reverse('library:delete-book', args=(9999,)))
        self.assertEqual(404, response.status_code)

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('library:delete-book', args=(2,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(url))

    def test_unauthorized(self):
        self.client.login(username='testuser', password='testpassword123')
        url = reverse('library:delete-book', args=(2,))
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)
        response = self.client.post(url)
        self.assertEqual(403, response.status_code)


class BorrowBookViewTest(TestCase):
    fixtures = ['books.json']

    @classmethod
    def setUpTestData(cls):
        create_test_users()
        cls.user = User.objects.get(username='testuser')
        cls.book = Book.objects.get(pk=1)

    def setUp(self):
        self.client.login(username='testuser', password='testpassword123')

    def test_success(self):
        response = self.client.post(reverse('library:borrow-book', args=(self.book.id,)))
        self.assertRedirects(response, reverse('library:book-list'))
        self.book.refresh_from_db()
        self.assertEqual(4, self.book.quantity)
        self.assertTrue(BorrowRecord.objects.filter(user=self.user, book=self.book).exists())
        borrow_record = BorrowRecord.objects.get(user=self.user, book=self.book)
        self.assertEqual(14, (borrow_record.due_date - timezone.now().date()).days)

    def test_fail(self):
        self.book.quantity = 0
        self.book.save()
        response = self.client.post(reverse('library:borrow-book', args=(self.book.id,)))
        self.assertRedirects(response, reverse('library:book-list'))
        self.book.refresh_from_db()
        self.assertEqual(0, self.book.quantity)
        self.assertFalse(BorrowRecord.objects.filter(user=self.user, book=self.book).exists())

    def test_unauthenticated(self):
        self.client.logout()
        borrow_url = reverse('library:borrow-book', args=(self.book.id,))
        response = self.client.post(borrow_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(borrow_url))


class BorrowRecordViewTest(TestCase):
    fixtures = ['books.json']

    @classmethod
    def setUpTestData(cls):
        create_test_users()
        cls.borrow_record = BorrowRecord.objects.create(user_id=1, book_id=1)

    def setUp(self):
        self.client.login(username='testuser', password='testpassword123')

    def test_borrow_record_list(self):
        response = self.client.get(reverse('library:borrow-records'))
        self.assertEqual(200, response.status_code)
        self.assertQuerySetEqual(response.context['borrow_record_list'], [self.borrow_record])

    def test_renew_book(self):
        original_due_date = self.borrow_record.due_date
        response = self.client.post(reverse('library:renew-book', args=(self.borrow_record.id,)))
        self.assertRedirects(response, reverse('library:borrow-records'))
        self.borrow_record.refresh_from_db()
        self.assertEqual(14, (self.borrow_record.due_date - original_due_date).days)

    def test_return_book(self):
        response = self.client.post(reverse('library:return-book', args=(self.borrow_record.id,)))
        self.assertRedirects(response, reverse('library:borrow-records'))
        self.borrow_record.refresh_from_db()
        self.assertEqual(timezone.now().date(), self.borrow_record.return_date)
        self.assertEqual(6, Book.objects.get(pk=1).quantity)

    def test_unauthenticated(self):
        self.client.logout()
        borrow_records_url = reverse('library:borrow-records')
        response = self.client.get(borrow_records_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(borrow_records_url))

        original_due_date = self.borrow_record.due_date
        renew_url = reverse('library:renew-book', args=(self.borrow_record.id,))
        response = self.client.post(renew_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(renew_url))
        self.borrow_record.refresh_from_db()
        self.assertEqual(original_due_date, self.borrow_record.due_date)

        return_url = reverse('library:return-book', args=(self.borrow_record.id,))
        response = self.client.post(return_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(return_url))
        self.borrow_record.refresh_from_db()
        self.assertIsNone(self.borrow_record.return_date)


class AdminBorrowRecordListViewTest(TestCase):
    fixtures = ['books.json']

    @classmethod
    def setUpTestData(cls):
        create_test_users()
        cls.user1_django = BorrowRecord.objects.create(user_id=1, book_id=1)
        cls.user1_python = BorrowRecord.objects.create(user_id=1, book_id=2)
        cls.user2_django = BorrowRecord.objects.create(user_id=2, book_id=1)

    def setUp(self):
        self.client.login(username='testadmin', password='testpassword789')

    def test_all_borrow_records(self):
        response = self.client.get(reverse('library:admin-borrow-records'))
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(response, 'library/admin_borrow_record_list.html')
        values = [self.user1_django, self.user1_python, self.user2_django]
        self.assertQuerySetEqual(response.context['borrow_record_list'], values, ordered=False)

    def test_search_by_username(self):
        response = self.client.get(reverse('library:admin-borrow-records'), {'username': 'testuser'})
        values = [self.user1_django, self.user1_python]
        self.assertQuerySetEqual(response.context['borrow_record_list'], values, ordered=False)

    def test_search_by_isbn(self):
        response = self.client.get(reverse('library:admin-borrow-records'), {'isbn': '9781735467269'})
        values = [self.user1_django, self.user2_django]
        self.assertQuerySetEqual(response.context['borrow_record_list'], values, ordered=False)

    def test_unauthenticated(self):
        self.client.logout()
        url = reverse('library:admin-borrow-records')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(url))

    def test_unauthorized(self):
        self.client.login(username='testuser', password='testpassword123')
        url = reverse('library:admin-borrow-records')
        response = self.client.get(url)
        self.assertEqual(403, response.status_code)

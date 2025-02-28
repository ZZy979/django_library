import datetime
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import dateformat

from .models import Book, BorrowRecord, Category


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


class UserLoginTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(username='testuser', password='testpassword123')

    def test_success(self):
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(reverse('library:login'), data)
        self.assertRedirects(response, reverse('library:search-book'))

    def test_fail(self):
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(reverse('library:login'), data)
        self.assertTemplateUsed(response, 'library/login.html')
        self.assertContains(response, 'Invalid username or password.')


class SearchBookViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.django = Book.objects.create(
            title='Django for Beginners', author='William S. Vincent', isbn='9781234567890')
        cls.python = Book.objects.create(
            title='Python Crash Course', author='Eric Matthes', isbn='9789876543210')
        for i in range(25):
            Book.objects.create(title=f'Book {i}', author=f'Author {i}', isbn=str(i))

    def test_search_by_title(self):
        response = self.client.get(reverse('library:search-book'), {'q': 'Django'})
        self.assertEqual(200, response.status_code)
        self.assertQuerySetEqual(response.context['book_list'], [self.django])

    def test_search_no_results(self):
        response = self.client.get(reverse('library:search-book'), {'q': 'Flask'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'No results found.')

    def test_pagination(self):
        response = self.client.get(reverse('library:search-book'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(20, len(response.context['book_list']))
        page_obj = response.context['page_obj']
        self.assertEqual(1, page_obj.number)
        self.assertEqual(2, page_obj.paginator.num_pages)

        response = self.client.get(reverse('library:search-book'), {'page': 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual(7, len(response.context['book_list']))
        self.assertEqual(2, response.context['page_obj'].number)

    def test_pagination_with_search(self):
        response = self.client.get(reverse('library:search-book'), {'q': 'Book', 'page': 2})
        self.assertEqual(200, response.status_code)
        self.assertEqual(5, len(response.context['book_list']))
        self.assertIn('q=Book', response.context['querystring'])


class BookDetailViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name='Programming')
        cls.book = Book.objects.create(
            title='Django for Beginners',
            author='William S. Vincent',
            isbn='9781234567890',
            publisher='WelcomeToCode',
            pub_date=datetime.date(2020, 8, 10),
            quantity=5,
            category=cls.category,
            description='A great book for learning Django.'
        )

    def test_book_detail(self):
        response = self.client.get(reverse('library:book-detail', args=(self.book.id,)))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book.author)
        self.assertContains(response, self.book.isbn)
        self.assertContains(response, self.book.publisher)
        self.assertContains(response, dateformat.format(self.book.pub_date, settings.DATE_FORMAT))
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.book.description)

    def test_not_found(self):
        response = self.client.get(reverse('library:book-detail', args=(9999,)))
        self.assertEqual(404, response.status_code)


class BorrowBookViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword123')
        cls.book = Book.objects.create(title='Test Book', author='Test Author', isbn='9781234567890', quantity=2)

    def setUp(self):
        self.client.login(username='testuser', password='testpassword123')

    def test_success(self):
        response = self.client.post(reverse('library:borrow-book', args=(self.book.id,)))
        self.assertRedirects(response, reverse('library:search-book'))
        self.assertEqual(1, Book.objects.get(id=self.book.id).quantity)
        self.assertTrue(BorrowRecord.objects.filter(user=self.user, book=self.book).exists())

    def test_fail(self):
        self.book.quantity = 0
        self.book.save()
        response = self.client.post(reverse('library:borrow-book', args=(self.book.id,)))
        self.assertRedirects(response, reverse('library:search-book'))
        self.assertEqual(0, Book.objects.get(id=self.book.id).quantity)
        self.assertFalse(BorrowRecord.objects.filter(user=self.user, book=self.book).exists())

    def test_unauthenticated(self):
        self.client.logout()
        borrow_url = reverse('library:borrow-book', args=(self.book.id,))
        response = self.client.post(borrow_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(borrow_url))


class ReturnBookViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpassword123')
        cls.book = Book.objects.create(title='Test Book', author='Test Author', isbn='9781234567890')
        cls.borrow_record = BorrowRecord.objects.create(user=cls.user, book=cls.book)

    def setUp(self):
        self.client.login(username='testuser', password='testpassword123')

    def test_success(self):
        response = self.client.get(reverse('library:borrow-records'))
        self.assertEqual(200, response.status_code)
        self.assertQuerySetEqual(response.context['borrow_record_list'], [self.borrow_record])

        response = self.client.post(reverse('library:return-book', args=(self.borrow_record.id,)))
        self.assertRedirects(response, reverse('library:borrow-records'))
        self.borrow_record.refresh_from_db()
        self.assertIsNotNone(self.borrow_record.return_date)
        self.assertEqual(2, Book.objects.get(id=self.book.id).quantity)

    def test_unauthenticated(self):
        self.client.logout()
        borrow_records_url = reverse('library:borrow-records')
        response = self.client.get(borrow_records_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(borrow_records_url))

        return_url = reverse('library:return-book', args=(self.borrow_record.id,))
        response = self.client.post(return_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(return_url))
        self.borrow_record.refresh_from_db()
        self.assertIsNone(self.borrow_record.return_date)

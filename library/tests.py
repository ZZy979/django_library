from urllib.parse import quote

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Book, BorrowRecord


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

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

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

    def setUp(self):
        self.django = Book.objects.create(
            title='Django for Beginners', author='William S. Vincent', isbn='9781234567890')
        self.python = Book.objects.create(
            title='Python Crash Course', author='Eric Matthes', isbn='9789876543210')

    def test_list_all(self):
        response = self.client.get(reverse('library:search-book'))
        self.assertEqual(200, response.status_code)
        self.assertQuerySetEqual(response.context['book_list'], Book.objects.all(), ordered=False)

    def test_search_by_title(self):
        response = self.client.get(reverse('library:search-book'), {'q': 'Django'})
        self.assertEqual(200, response.status_code)
        self.assertQuerySetEqual(response.context['book_list'], [self.django])

    def test_search_no_results(self):
        response = self.client.get(reverse('library:search-book'), {'q': 'Flask'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'No results found.')


class BorrowBookViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')
        self.book = Book.objects.create(title='Test Book', author='Test Author', isbn='9781234567890', quantity=2)
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

    def test_not_login(self):
        self.client.logout()
        borrow_url = reverse('library:borrow-book', args=(self.book.id,))
        response = self.client.post(borrow_url)
        self.assertRedirects(response, reverse('library:login') + '?next=' + quote(borrow_url))

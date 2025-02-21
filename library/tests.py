from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Book, BorrowRecord


class UserLoginTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword123')

    def test_login_success(self):
        data = {'username': 'testuser', 'password': 'testpassword123'}
        response = self.client.post(reverse('library:login'), data)
        self.assertRedirects(response, reverse('library:search-book'))

    def test_login_fail(self):
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

    def test_borrow_success(self):
        response = self.client.post(reverse('library:borrow-book', args=(self.book.id,)))
        self.assertRedirects(response, reverse('library:search-book'))
        self.assertEqual(1, Book.objects.get(id=self.book.id).quantity)
        self.assertTrue(BorrowRecord.objects.filter(user=self.user, book=self.book).exists())

    def test_borrow_fail(self):
        self.book.quantity = 0
        self.book.save()
        response = self.client.post(reverse('library:borrow-book', args=(self.book.id,)))
        self.assertRedirects(response, reverse('library:search-book'))
        self.assertEqual(0, Book.objects.get(id=self.book.id).quantity)
        self.assertFalse(BorrowRecord.objects.filter(user=self.user, book=self.book).exists())

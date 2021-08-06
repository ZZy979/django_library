from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from .models import User, Reader, Librarian, Author, Book


def create_test_user_and_group():
    reader_group = Group.objects.create(name=settings.READER_GROUP)
    librarian_group = Group.objects.create(name=settings.LIBRARIAN_GROUP)

    alice = User.objects.create_user('alice', 'alice@example.com', '1234')
    alice.groups.add(librarian_group)
    Librarian.objects.create(user=alice)
    bob = User.objects.create_user('bob', 'bob@example.com', '1234')
    bob.groups.add(reader_group)
    Reader.objects.create(user=bob)
    User.objects.create_user('guest', 'guest@example.com', '1234')


class UserModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()

    def test_can_login(self):
        tests = [
            ('alice', False, True, True),
            ('bob', True, False, True),
            ('guest', False, False, False)
        ]
        for username, is_reader, is_librarian, can_login in tests:
            user = User.objects.get(username=username)
            self.assertEqual(is_reader, user.is_reader())
            self.assertEqual(is_librarian, user.is_librarian())
            self.assertEqual(can_login, user.can_login())


class RegisterViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_user_and_group()

    def test_get(self):
        response = self.client.get(reverse('library:register'))
        self.assertTemplateUsed(response, 'library/register.html')

    def test_invalid_username(self):
        data = {'username': '@#%', 'password': '1234', 'password2': '1234'}
        response = self.client.post(reverse('library:register'), data)
        self.assertEqual('用户名只能包含字母、数字和下划线', response.context['message'])

    def test_username_already_exists(self):
        data = {'username': 'alice', 'password': '1234', 'password2': '1234'}
        response = self.client.post(reverse('library:register'), data)
        self.assertEqual('用户名已存在', response.context['message'])

    def test_passwords_not_match(self):
        data = {'username': 'cindy', 'password': '1234', 'password2': '5678'}
        response = self.client.post(reverse('library:register'), data)
        self.assertEqual('两次密码不一致', response.context['message'])

    def test_ok(self):
        data = {'username': 'cindy', 'password': '1234', 'password2': '1234', 'name': '', 'email': ''}
        response = self.client.post(reverse('library:register'), data)
        self.assertRedirects(response, reverse('library:index'))
        cindy = User.objects.get(username='cindy')
        self.assertTrue(cindy.is_reader())
        self.assertFalse(cindy.is_librarian())
        self.assertTrue(Reader.objects.filter(user=cindy).exists())


def create_test_author_and_book():
    twain = Author.objects.create(name='Mark Twain', country='America')
    swift = Author.objects.create(name='Jonathan Swift', country='England')

    Book.objects.create(author=twain, title='The Adventures of Tom Sawyer', isbn='', publisher='', price=0)
    Book.objects.create(author=twain, title='The Adventures of Huckleberry Finn', isbn='', publisher='', price=0)
    Book.objects.create(author=swift, title="Gulliver's Travels", isbn='', publisher='', price=0)


class SearchBookViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_author_and_book()

    def test_search_book(self):
        response = self.client.get(reverse('library:search-book'), {'title': 'adventures'})
        self.assertEqual(200, response.status_code)
        expected = ['<Book: The Adventures of Tom Sawyer>', '<Book: The Adventures of Huckleberry Finn>']
        self.assertQuerysetEqual(response.context['book_list'], expected, ordered=False)

    def test_no_result(self):
        response = self.client.get(reverse('library:search-book'), {'title': 'xxx'})
        self.assertContains(response, '没有符合条件的图书')
        self.assertQuerysetEqual(response.context['book_list'], [])


class SearchAuthorViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_author_and_book()

    def test_search_author(self):
        response = self.client.get(reverse('library:search-author'), {'name': 'Swift'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['author_list'], ['<Author: Jonathan Swift>'])

    def test_no_result(self):
        response = self.client.get(reverse('library:search-author'), {'name': 'xxx'})
        self.assertContains(response, '没有符合条件的作者')
        self.assertQuerysetEqual(response.context['author_list'], [])


class BookDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_author_and_book()

    def test_ok(self):
        book = Book.objects.get(pk=1)
        response = self.client.get(reverse('library:book-detail', args=(1,)))
        self.assertEqual(200, response.status_code)
        self.assertContains(response, book.title)

    def test_not_found(self):
        response = self.client.get(reverse('library:book-detail', args=(999,)))
        self.assertEqual(404, response.status_code)


class AuthorDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_author_and_book()

    def test_ok(self):
        author = Author.objects.get(pk=1)
        response = self.client.get(reverse('library:author-detail', args=(1,)))
        self.assertContains(response, author.name)
        self.assertContains(response, author.country)

    def test_not_found(self):
        response = self.client.get(reverse('library:author-detail', args=(999,)))
        self.assertEqual(404, response.status_code)


class BooksOfAuthorViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        create_test_author_and_book()

    def test_query_books_of_author(self):
        response = self.client.get(reverse('library:books-of-author'), {'aid': 1})
        self.assertEqual(response.status_code, 200)
        expected = ['<Book: The Adventures of Tom Sawyer>', '<Book: The Adventures of Huckleberry Finn>']
        self.assertQuerysetEqual(response.context['book_list'], expected, ordered=False)

    def test_no_such_author(self):
        response = self.client.get(reverse('library:books-of-author'), {'aid': 9999})
        self.assertEqual(response.status_code, 404)

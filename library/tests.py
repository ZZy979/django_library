from django.test import TestCase
from django.urls import reverse

from .models import Author, Book


class AuthorListViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Author.objects.create(name='Alice', country='America')
        Author.objects.create(name='Bob', country='China')

    def test_query_author(self):
        """根据姓名查询作者。"""
        response = self.client.get(reverse('library:search-author'), {'name': 'Alice'})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['author_list'], ['<Author: Alice>'])

    def test_not_found(self):
        """未查询到作者。"""
        response = self.client.get(reverse('library:search-author'), {'name': 'Cindy'})
        self.assertContains(response, '没有符合条件的作者')
        self.assertQuerysetEqual(response.context['author_list'], [])


class AuthorDetailViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.alice = Author.objects.create(name='Alice', country='America')
        cls.bob = Author.objects.create(name='Bob', country='China')

    def test_author_detail(self):
        """查询作者详细信息。"""
        response = self.client.get(reverse('library:author-detail', args=(self.alice.id,)))
        self.assertContains(response, self.alice.name)
        self.assertContains(response, self.alice.country)

    def test_not_found(self):
        """作者id不存在。"""
        response = self.client.get(reverse('library:author-detail', args=(9999,)))
        self.assertEqual(response.status_code, 404)


class BooksOfAuthorViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.alice = Author.objects.create(name='Alice', country='America')
        cls.bob = Author.objects.create(name='Bob', country='China')
        Book.objects.create(author=cls.alice, title='foo', isbn='111', publisher='A', price=5)
        Book.objects.create(author=cls.alice, title='bar', isbn='222', publisher='B', price=6)
        Book.objects.create(author=cls.bob, title='baz', isbn='333', publisher='C', price=7)
        Book.objects.create(author=cls.bob, title='qux', isbn='444', publisher='A', price=8)
        Book.objects.create(author=cls.bob, title='xyzzy', isbn='555', publisher='C', price=9)

    def test_query_books_of_author(self):
        """查询作者所著图书。"""
        response = self.client.get(reverse('library:books-of-author'), {'aid': self.bob.id})
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['book_list'],
            ['<Book: baz>', '<Book: qux>', '<Book: xyzzy>'],
            ordered=False
        )

    def test_no_such_author(self):
        """作者id不存在。"""
        response = self.client.get(reverse('library:books-of-author'), {'aid': 9999})
        self.assertEqual(response.status_code, 404)

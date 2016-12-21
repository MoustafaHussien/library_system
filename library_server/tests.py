from django.core.management import call_command
from django.test import Client
from django.test import TestCase


class LibrarySystemTest(TestCase):
    def setUp(self):
        call_command('loaddata', 'library_server/fixtures/test_data.json', verbosity=0)

    def test_database_and_user_login(self):
        self.assertTrue(self.client.login(username='jacob', password='password1'))
        self.assertFalse(self.client.login(username='jacob', password='wrong password'))

    def test_user_login_successful(self):
        c = Client()
        response = c.post('/accounts/login/', {'username': 'jacob', 'password': 'password1'})
        self.assertRedirects(response, '/accounts/profile/')
        self.assertEqual(response.status_code, 302)

    def test_user_login_failure(self):
        c = Client()
        response = c.post('/accounts/login/', {'password': 'wrong_password'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertFormError(response, 'form', 'username', 'This field is required.')
        response = c.post('/accounts/login/', {'username': 'jacob'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertFormError(response, 'form', 'password', 'This field is required.')
        response = c.post('/accounts/login/', {'username': 'jacob', 'password': 'wrong_password'})
        self.assertContains(response, "Your username and password didn't match. Please try again.", 1, 200)

    def test_user_registration_for_authenticated_user(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/registration/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/main_page')

    def test_user_registration_for_unauthenticated_user(self):
        c = Client()
        response = c.get('/registration/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library_server/registration.html')

    def test_user_registration_form(self):
        c = Client()
        response = c.post('/registration/', {'username': 'jacob', 'email': 'dummy_mail'})
        self.assertFormError(response, 'form', 'email', 'Enter a valid email address.')
        response = c.post('/registration/', {'username': 'jacob', 'email': 'dummy_mail@yahoo.com'})
        self.assertFormError(response, 'form', 'password1', 'This field is required.')
        response = c.post('/registration/', {'username': 'jacob', 'email': 'dummy_mail@yahoo.com', 'password1': 'my_secret'})
        self.assertFormError(response, 'form', 'password2', 'This field is required.')
        response = c.post('/registration/',
                          {'username': 'jacob', 'email': 'dummy_mail@yahoo.com', 'password1': 'my_secret', 'password2': 'not my_secret'})
        self.assertContains(response, "The two password fields didn&#39;t match.", 1, 200)
        self.assertContains(response, "A user with that username already exists.", 1, 200)
        response = c.post('/registration/',
                          {'username': 'Nic', 'email': 'dummy_mail@yahoo.com', 'password1': 'my_secret', 'password2': 'my_secret'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/main_page')

    def test_user_borrow_for_unauthenticated_user(self):
        c = Client()
        response = c.get('/borrow/1/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/borrow/1/')

    def test_user_borrow_for_authenticated_user(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/borrow/200/')
        self.assertEqual(response.status_code, 404)
        response = c.get('/borrow/1/')
        self.assertContains(response, "book borrowing successful", 1, 200)
        response = c.get('/borrow/1/')
        self.assertContains(response, "Ali has already borrowed that book before", 1, 200)

    def test_view_book_details_for_unauthenticated_user(self):
        c = Client()
        response = c.get('/books/200/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/books/200/')

    def test_view_book_details_for_authenticated_user(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/books/200/')
        self.assertEqual(response.status_code, 404)
        response = c.get('/books/2/')
        self.assertContains(response, "Title : Diary of a Wimpy Kid # 11: Double Down", 1, 200)
        self.assertContains(response, "ISBN : 978-1419723445", 1, 200)

    def test_user_borrow_for_authenticated_user_no_avail_copies(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/borrow/3/')
        self.assertContains(response, "Sorry there is no available copies at the moment", 1, 200)
        self.assertContains(response, "Your request has been saved and will be updated automatically", 1, 200)

    def test_user_return_book_for_authenticated_user(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/borrow/1/')
        self.assertContains(response, "book borrowing successful", 1, 200)
        response = c.get('/return/1/')
        self.assertContains(response, "book return successful", 1, 200)

    def test_user_return_unborrowed_book_for_authenticated_user(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/return/1/')
        self.assertContains(response, "Ali didn't borrow that book", 1, 200)

    def test_user_return_book_not_existing(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/return/10/')
        self.assertEqual(response.status_code, 404)

    def test_user_return_book_for_unauthenticated_user(self):
        c = Client()
        response = c.get('/borrow/1/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/borrow/1/')
        response = c.get('/return/1/')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/return/1/')

    def test_user_search_for_book1(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/search/', {'search_box': 'Whistler'})
        self.assertContains(response, "The Whistler", 1, 200)

    def test_user_search_for_book2(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/search/', {'search_box': '978-1481466226'})
        self.assertContains(response, "Take Heart  My Child: A Mother&#39;s Dream", 1, 200)

    def test_user_search_for_book3(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/search/', {'search_box': 'Bill'})
        self.assertContains(response, "Killing the Rising Sun: How America Vanquished World War II Japan", 1, 200)

    def test_user_search_for_book4(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/search/', {'search_box': 'Revolution'})
        self.assertContains(response, "Hamilton: The Revolution", 1, 200)
        self.assertContains(response, "Our Revolution: A Future to Believe In", 1, 200)

    def test_user_search_for_book5(self):
        c = Client()
        c.post('/accounts/login/', {'username': 'Ali', 'password': 'password2'})
        response = c.get('/search/', {'search_box': 'the'})
        self.assertContains(response, "Fantastic Beasts and Where to Find Them: The Original Screenplay", 1, 200)
        self.assertContains(response, "The Magnolia Story", 1, 200)
        self.assertContains(response, "Killing the Rising Sun: How America Vanquished World War II Japan", 1, 200)
        self.assertContains(response, "Take Heart  My Child: A Mother&#39;s Dream", 1, 200)
        self.assertContains(response, "Hamilton: The Revolution", 1, 200)
        self.assertContains(response, "The Whistler", 1, 200)

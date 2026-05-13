from django.contrib.auth.models import User
from django.test import TestCase, Client
from projecte.games.models import Wishlist, SteamGame, Comment

# Create your tests here.

class WishlistE2ETest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@gmail.com', password='123456789')
        self.client.login(username='testuser', password='123456789')
        self.game = SteamGame.objects.create(steam_id=1, name='test', price='20', url='http://test')

    def test_add_game_to_wishlist(self):
        response = self.client.post(f'/wishlist/toggle/{self.game.steam_id}/')

        self.assertEqual(response.status_code, 302)
        wishlist = Wishlist.objects.get(user=self.user)
        self.assertTrue(wishlist.games.filter(id=self.game.steam_id).exists())

    def test_remove_game_from_wishlist(self):
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.games.add(self.game)

        response = self.client.post(f'/wishlist/toggle/{self.game.steam_id}/')

        self.assertEqual(response.status_code, 302)
        self.assertFalse(wishlist.games.filter(id=self.game.steam_id).exists())

class CommentE2ETest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@gmail.com', password='123456789')
        self.client.login(username='testuser', password='123456789')
        self.game = SteamGame.objects.create(steam_id=1, name='test', price='20', url='http://test')

    def test_add_comment_to_game(self):
        response = self.client.post(f'/game/{self.game.steam_id}/',{'content': 'peak gaming'})

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(
                user=self.user,
                game=self.game,
                content='peak gaming'
            ).exists()
        )

    def test_edit_comment_from_game(self):
        comment= Comment.objects.create(
            user=self.user,
            game=self.game,
            content='peak gaming'
        )
        response = self.client.post(f'/comment/edit/{comment.id}/', {'content': 'this game is a 10/10'})

        self.assertEqual(response.status_code, 302)
        comment.refresh_from_db()

        self.assertEqual(comment.content,'this game is a 10/10')

    def test_delete_comment_from_game(self):
        comment = Comment.objects.create(
            user=self.user,
            game=self.game,
            content='too expensive D:<'
        )

        response = self.client.post(f'/comment/delete/{comment.id}/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(id=comment.id).exists())
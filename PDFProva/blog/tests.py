from django.test import TestCase
from .models import Post  # Assuming you have a Post model in blog/models.py

class BlogModelTests(TestCase):

    def test_post_creation(self):
        post = Post.objects.create(title="Test Post", content="This is a test post.")
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.content, "This is a test post.")
        self.assertIsNotNone(post.created_at)  # Assuming you have a created_at field

    def test_post_str(self):
        post = Post(title="Test Post")
        self.assertEqual(str(post), "Test Post")  # Assuming __str__ method returns title

    # Add more tests as needed for your blog functionality
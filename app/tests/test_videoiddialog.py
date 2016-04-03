import unittest

from app.videoiddialog import VideoIDDialog


class VideoIDDialogTests(unittest.TestCase):
    """Tests for the app.videoiddialog module"""

    def test_get_id_from_url(self):
        """Test VideoIDDialog.get_id_from_url function"""
        urls = [
            'http://www.youtube.com/user/dreamtheater#p/u/1/oTJRivZTMLs',
            'https://youtu.be/oTJRivZTMLs?list=PLToa5JuFMsXTNkrLJbRlB--76IAOjRM9b',
            'http://www.youtube.com/watch?v=oTJRivZTMLs&feature=youtu.be',
            'https://youtu.be/oTJRivZTMLs',
            'http://youtu.be/oTJRivZTMLs&feature=channel',
            'http://www.youtube.com/ytscreeningroom?v=oTJRivZTMLs',
            'http://www.youtube.com/embed/oTJRivZTMLs?rel=0',
            'http://youtube.com/v/oTJRivZTMLs&feature=channel',
            'http://youtube.com/v/oTJRivZTMLs&feature=channel',
            'http://youtube.com/vi/oTJRivZTMLs&feature=channel',
            'http://youtube.com/?v=oTJRivZTMLs&feature=channel',
            'http://youtube.com/?feature=channel&v=oTJRivZTMLs',
            'http://youtube.com/?vi=oTJRivZTMLs&feature=channel',
            'http://youtube.com/watch?v=oTJRivZTMLs&feature=channel',
            'http://youtube.com/watch?vi=oTJRivZTMLs&feature=channel'
        ]
        for url in urls:
            self.assertEqual(VideoIDDialog.get_id_from_url(url), 'oTJRivZTMLs', msg=url)

        invalid_urls = [
            'foobar',
            'http://google.com/?v=oTJRivZTMLs',
            'http://google.com/v/oTJRivZTMLs',
            'oTJRivZTMLs'
        ]
        for url in invalid_urls:
            self.assertRaises(ValueError, VideoIDDialog.get_id_from_url, url)

#
# This file is part of Plinth.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Test module for Plinth's utilities.
"""

from unittest.mock import Mock, MagicMock

from django.test import TestCase
from django.test.client import RequestFactory

from plinth.utils import is_user_admin


class TestIsAdminUser(TestCase):
    """Test class for is_user_admin utility."""

    def setUp(self):
        """Setup each test case befor execution."""
        request = RequestFactory().get('/plinth/mockapp')
        request.user = Mock()
        request.session = MagicMock()
        self.request = request

    def test_is_false_for_anonymous_user(self):
        """Test anonymous user is reported as non-admin."""
        super(TestIsAdminUser, self).setUp()
        self.request.user = Mock()
        self.request.user.is_authenticated.return_value = False
        self.assertFalse(is_user_admin(self.request))
        self.assertFalse(is_user_admin(self.request, cached=True))

    def test_values_for_authenticated_users(self):
        """Test correct return values for authenticated users."""
        self.request.user.groups.filter().exists = Mock(return_value=False)
        self.assertFalse(is_user_admin(self.request))
        self.request.user.groups.filter().exists = Mock(return_value=True)
        self.assertTrue(is_user_admin(self.request))

    def test_caching_of_values(self):
        """Test that caching of values for authenticate users."""
        session_mock = MagicMock()
        session_dict = {}
        session_mock.__setitem__.side_effect = session_dict.__setitem__
        session_mock.__getitem__.side_effect = session_dict.__getitem__
        session_mock.__contains__.side_effect = session_dict.__contains__
        self.request.session = session_mock

        mock = Mock(return_value=False)
        self.request.user.groups.filter().exists = mock
        self.assertFalse(is_user_admin(self.request))
        mock.assert_called_once_with()
        session_mock.__setitem__.assert_called_once_with(
            'cache_user_is_admin', False)

        mock = Mock(return_value=False)
        self.request.user.groups.filter().exists = mock
        self.assertFalse(is_user_admin(self.request, cached=True))
        mock.assert_not_called()
        session_mock.__getitem__.assert_called_once_with(
            'cache_user_is_admin')

        mock = Mock(return_value=False)
        self.request.user.groups.filter().exists = mock
        self.assertFalse(is_user_admin(self.request, cached=False))
        mock.assert_called_once_with()
        session_mock.__getitem__.assert_called_once_with(
            'cache_user_is_admin')

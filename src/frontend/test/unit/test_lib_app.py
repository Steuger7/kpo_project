import pytest
from unittest.mock import Mock, patch, PropertyMock, MagicMock, call
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from LibApp import LibApp, MainGridContainer
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise


class TestLibAppComposeAndMount:
    
    def test_compose(self):
        app = LibApp()
        
        with patch('LibApp.App.__init__'):
            app = LibApp()
            
            compose_result = list(app.compose())
            
            assert app.main_container is not None
            assert isinstance(app.main_container, MainGridContainer)
            assert app.main_container.id == "main-grid-container"
            assert app.main_container.styles.display == "none"
    
    def test_on_mount(self):
        app = LibApp()
        
        mock_book1 = Mock()
        mock_book1.set_focus_handler = Mock()
        mock_book2 = Mock()
        mock_book2.set_focus_handler = Mock()
        
        app.book_containers = [mock_book1, mock_book2]
        
        with patch.object(app, 'showMainContainer') as mock_show:
            with patch.object(app, 'has_saved_user') as mock_has_user:
                mock_has_user.return_value = False
                
                app.on_mount()
                
                mock_book1.set_focus_handler.assert_called_once_with(app._on_book_focused)
                mock_book2.set_focus_handler.assert_called_once_with(app._on_book_focused)
                
                mock_show.assert_called_once()
    
    def test_on_mount_with_auto_login(self):
        app = LibApp()
        
        with patch.object(app, 'showMainContainer') as mock_show:
            with patch.object(app, 'has_saved_user') as mock_has_user:
                with patch.object(app, 'attempt_auto_login') as mock_auto_login:
                    mock_has_user.return_value = True
                    
                    app.on_mount()
                    
                    mock_auto_login.assert_called_once()
                    mock_show.assert_called_once()


class TestLibAppSearchMethods:
    
    def test_search_books_success(self):
        app = LibApp()
        
        test_query = "python programming"
        mock_response_data = {
            'docs': [
                {
                    'title': 'Python Cookbook',
                    'author_name': ['David Beazley', 'Brian Jones'],
                    'first_publish_year': 2013,
                    'cover_i': 12345,
                    'key': '/works/OL12345W',
                    'language': ['eng']
                }
            ]
        }
        
        with patch('LibApp.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response
            
            with patch.object(app, 'display_books') as mock_display:
                app.search_books(test_query)
                
                expected_url = f"{app.search_api}?q=python+programming"
                mock_get.assert_called_once_with(expected_url)
                
                mock_display.assert_called_once_with(mock_response_data['docs'])
    
    def test_search_books_failure(self):
        app = LibApp()
        
        with patch('LibApp.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            with patch.object(app, 'display_books') as mock_display:
                app.search_books("test query")
                
                mock_display.assert_not_called()
    
    def test_search_books_bad_status(self):
        app = LibApp()
        
        with patch('LibApp.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response
            
            with patch.object(app, 'display_books') as mock_display:
                app.search_books("test query")
                
                mock_display.assert_not_called()
    
    def test_search_personal_library_success(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        test_query = "python"
        mock_response_data = {
            'success': True,
            'books': [
                {
                    'title': 'Python Basics',
                    'author': 'John Doe',
                    'year': 2020,
                    'key': 'python_basics_123'
                }
            ]
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            with patch.object(app, 'display_books') as mock_display:
                app.search_personal_library(test_query)
                
                expected_url = f"{app.base_url}/lib"
                expected_data = {
                    "userid": "test_user",
                    "password": "test_pass",
                    "query": test_query
                }
                mock_post.assert_called_once_with(expected_url, json=expected_data)
                
                mock_display.assert_called_once_with(mock_response_data['books'])
    
    def test_search_personal_library_no_credentials(self):
        app = LibApp()
        app.userid = None
        app.password = None
        
        with patch('LibApp.requests.post') as mock_post:
            app.search_personal_library("test query")
            
            mock_post.assert_not_called()
    
    def test_search_personal_library_failure(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        with patch('LibApp.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            app.search_personal_library("test query")


class TestLibAppDisplayBooks:
    
    def test_display_books_success(self):
        app = LibApp()
        
        books_data = [
            {
                'title': 'Book 1',
                'author_name': ['Author 1'],
                'first_publish_year': 2000,
                'cover_i': 1001,
                'key': '/works/OL1001W',
                'language': ['eng']
            },
            {
                'title': 'Book 2',
                'author_name': ['Author 2', 'Co-Author'],
                'first_publish_year': 2010,
                'cover_i': 1002,
                'key': '/works/OL1002W',
                'language': ['rus']
            }
        ]
        
        mock_right_pane = Mock()
        mock_right_pane.mount = Mock()
        
        with patch.object(app, 'query_one') as mock_query:
            mock_query.return_value = mock_right_pane
            
            with patch('LibApp.BookContainer') as MockBookContainer:
                mock_container1 = Mock()
                mock_container1.set_focus_handler = Mock()
                mock_container2 = Mock()
                mock_container2.set_focus_handler = Mock()
                
                MockBookContainer.side_effect = [mock_container1, mock_container2]
                
                with patch.object(app, 'is_book_in_library') as mock_is_in_lib:
                    mock_is_in_lib.side_effect = [False, True]
                    
                    app.display_books(books_data)
                    
                    assert MockBookContainer.call_count == 2
                    
                    first_call_args = MockBookContainer.call_args_list[0]
                    first_book_data = first_call_args[0][0]  # Первый аргумент - book
                    
                    assert first_book_data['title'] == 'Book 1'
                    assert first_book_data['author'] == 'Author 1'
                    assert first_book_data['year'] == 2000
                    assert first_book_data['cover_i'] == 1001
                    assert first_book_data['key'] == '/works/OL1001W'
                    assert first_book_data['language'] == ['eng']
                    
                    second_call_kwargs = MockBookContainer.call_args_list[1][1]
                    assert second_call_kwargs['is_added'] is True
                    
                    assert len(app.book_containers) == 2
                    assert mock_container1 in app.book_containers
                    assert mock_container2 in app.book_containers
                    
                    mock_container1.set_focus_handler.assert_called_once_with(app._on_book_focused)
                    mock_container2.set_focus_handler.assert_called_once_with(app._on_book_focused)
                    
                    assert mock_right_pane.mount.call_count == 2
    
    def test_display_books_empty_data(self):
        app = LibApp()
        
        mock_old_container = Mock()
        mock_old_container.remove = Mock()
        app.book_containers = [mock_old_container]
        
        mock_right_pane = Mock()
        
        with patch.object(app, 'query_one') as mock_query:
            mock_query.return_value = mock_right_pane
            
            app.display_books([])
            
            mock_old_container.remove.assert_called_once()
            assert len(app.book_containers) == 0
    
    def test_display_books_missing_fields(self):
        app = LibApp()
        
        books_data = [
            {
                'title': 'Book with minimal data'
            }
        ]
        
        mock_right_pane = Mock()
        
        with patch.object(app, 'query_one') as mock_query:
            mock_query.return_value = mock_right_pane
            
            with patch('LibApp.BookContainer') as MockBookContainer:
                mock_container = Mock()
                mock_container.set_focus_handler = Mock()
                MockBookContainer.return_value = mock_container
                
                app.display_books(books_data)
                
                call_args = MockBookContainer.call_args[0][0]  # book dict
                
                assert call_args['title'] == 'Book with minimal data'
                assert call_args['author'] == 'Неизвестен'
                assert call_args['year'] == 'Неизвестен'
                assert call_args['cover_i'] == 0
                assert call_args['key'] == ''
                assert call_args['language'] == ''


class TestLibAppBookFocusNavigation:
    
    def test_on_book_focused(self):
        app = LibApp()
        
        mock_book_container = Mock()
        
        app._on_book_focused(mock_book_container)
        
        assert app.last_focused_book == mock_book_container
    
    def test_action_focus_next_book_with_focus(self):
        app = LibApp()
        
        mock_book1 = Mock()
        mock_book2 = Mock()
        mock_book3 = Mock()
        app.book_containers = [mock_book1, mock_book2, mock_book3]
        
        with patch.object(app, 'is_focus_on_books') as mock_is_focus:
            mock_is_focus.return_value = True
            
            with patch.object(app, 'get_current_book_index') as mock_get_index:
                mock_get_index.return_value = 1
                
                app.action_focus_next_book()
                
                mock_book2.focus.assert_not_called()  # Текущая
                mock_book3.focus.assert_called_once()  # Следующая
    
    def test_action_focus_next_book_without_focus(self):
        app = LibApp()
        
        mock_book1 = Mock()
        mock_book2 = Mock()
        app.book_containers = [mock_book1, mock_book2]
        app.last_focused_book = mock_book2
        
        with patch.object(app, 'is_focus_on_books') as mock_is_focus:
            mock_is_focus.return_value = False
            
            app.action_focus_next_book()
            
            mock_book2.focus.assert_called_once()
    
    def test_action_focus_next_book_without_focus_no_last(self):
        app = LibApp()
        
        mock_book1 = Mock()
        mock_book2 = Mock()
        app.book_containers = [mock_book1, mock_book2]
        app.last_focused_book = None
        
        with patch.object(app, 'is_focus_on_books') as mock_is_focus:
            mock_is_focus.return_value = False
            
            app.action_focus_next_book()
            
            mock_book1.focus.assert_called_once()
    
    def test_action_focus_previous_book_wrap_around(self):
        app = LibApp()
        
        mock_book1 = Mock()
        mock_book2 = Mock()
        mock_book3 = Mock()
        app.book_containers = [mock_book1, mock_book2, mock_book3]
        
        with patch.object(app, 'is_focus_on_books') as mock_is_focus:
            mock_is_focus.return_value = True
            
            with patch.object(app, 'get_current_book_index') as mock_get_index:
                mock_get_index.return_value = 0  # Первая книга
                
                app.action_focus_previous_book()
                
                mock_book3.focus.assert_called_once()


class TestLibAppNetworkAPIMethods:
    
    def test_add_book_to_library_success(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        book = {
            'title': 'Test Book',
            'author': 'Test Author',
            'year': 2023,
            'cover_i': 12345,
            'key': '/works/OL12345W',
            'language': 'eng'
        }
        
        mock_response_data = {
            'success': True,
            'message': 'Book added'
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            with patch.object(app, '_update_library_keys_full') as mock_update:
                with patch.object(app, 'update_user_info_display') as mock_update_display:
                    result = app.add_book_to_library(book)
                    
                    expected_url = f"{app.base_url}/lib/addbook"
                    expected_data = {
                        "userid": "test_user",
                        "password": "test_pass",
                        "cover_i": 12345,
                        "first_year_publish": 2023,
                        "key": '/works/OL12345W',
                        "language": 'eng',
                        "title": 'Test Book'
                    }
                    mock_post.assert_called_once_with(expected_url, json=expected_data, timeout=10)
                    
                    mock_update.assert_called_once()
                    mock_update_display.assert_called_once()
                    
                    assert result is True
    
    def test_add_book_to_library_failure(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        book = {
            'title': 'Test Book',
            'key': '/works/OL12345W'
        }
        
        mock_response_data = {
            'success': False,
            'message': 'Error'
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = app.add_book_to_library(book)
            
            assert result is False
    
    def test_add_book_to_library_no_credentials(self):
        app = LibApp()
        app.userid = None
        app.password = None
        
        book = {'title': 'Test Book'}
        
        result = app.add_book_to_library(book)
        
        assert result is False
    
    def test_add_book_to_library_network_error(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        with patch('LibApp.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            result = app.add_book_to_library({'title': 'Test Book'})
            
            assert result is False
    
    def test_remove_book_from_library_success(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        book = {
            'key': '/works/OL12345W',
            'title': 'Test Book'
        }
        
        mock_response_data = {
            'success': True,
            'message': 'Book removed'
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            with patch.object(app, '_update_library_keys_full') as mock_update:
                with patch.object(app, 'update_user_info_display') as mock_update_display:
                    result = app.remove_book_from_library(book)
                    
                    expected_url = f"{app.base_url}/lib/removebook"
                    expected_data = {
                        "userid": "test_user",
                        "password": "test_pass",
                        "key": '/works/OL12345W'
                    }
                    mock_post.assert_called_once_with(expected_url, json=expected_data, timeout=10)
                    
                    mock_update.assert_called_once()
                    mock_update_display.assert_called_once()
                    
                    assert result is True
    
    def test_remove_book_from_library_failure(self):
        app = LibApp()
        
        book = {'key': '/works/OL12345W'}
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response
            
            result = app.remove_book_from_library(book)
            
            assert result is False


class TestLibAppLoginMethods:
    
    def test_handle_login_backend_success(self):
        app = LibApp()
        
        username = "test_user"
        password = "test_pass"
        
        mock_response_data = {
            'success': True,
            'userid': 'user123',
            'message': 'Login successful'
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = app._handle_login_backend(username, password)
            
            expected_url = f"{app.base_url}/login"
            expected_data = {
                "username": username,
                "password": password
            }
            mock_post.assert_called_once_with(expected_url, json=expected_data)
            
            assert app.current_user == username
            assert app.userid == 'user123'
            assert app.password == password
            
            assert result is True
    
    def test_handle_login_backend_failure(self):
        app = LibApp()
        
        mock_response_data = {
            'success': False,
            'message': 'Invalid credentials'
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = app._handle_login_backend("user", "pass")
            
            assert result is False
            assert app.current_user == "Гость"  # Не изменился
    
    def test_handle_login_backend_network_error(self):
        app = LibApp()
        
        with patch('LibApp.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            result = app._handle_login_backend("user", "pass")
            
            assert result is False
    
    def test_handle_register_backend_success(self):
        app = LibApp()
        
        username = "new_user"
        password = "new_pass"
        
        mock_response_data = {
            'success': True,
            'userid': 'newuser123',
            'message': 'Registration successful'
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            result = app._handle_register_backend(username, password)
            
            assert app.current_user == username
            assert app.userid == 'newuser123'
            assert app.password == password
            
            assert result is True
    
    def test_attempt_auto_login_success(self):
        app = LibApp()
        
        with patch.object(app, 'get_saved_credentials') as mock_get_creds:
            mock_get_creds.return_value = ("saved_user", "saved_pass")
            
            with patch.object(app, '_handle_login_backend') as mock_login:
                mock_login.return_value = True
                
                with patch.object(app, '_update_library_keys_full') as mock_update:
                    with patch.object(app, 'showMainContainer') as mock_show:
                        with patch.object(app, 'update_user_info_display') as mock_update_display:
                            app.attempt_auto_login()
                            
                            mock_get_creds.assert_called_once()
                            mock_login.assert_called_once_with("saved_user", "saved_pass")
                            mock_update.assert_called_once()
                            mock_show.assert_called_once()
                            mock_update_display.assert_called_once()
                            
                            assert app.auto_login_attempted is True
    
    def test_attempt_auto_login_no_credentials(self):
        app = LibApp()
        
        with patch.object(app, 'get_saved_credentials') as mock_get_creds:
            mock_get_creds.return_value = None
            
            with patch.object(app, '_handle_login_backend') as mock_login:
                with patch.object(app, 'showMainContainer') as mock_show:
                    with patch.object(app, 'update_user_info_display') as mock_update_display:
                        app.attempt_auto_login()
                        
                        mock_login.assert_not_called()
                        mock_show.assert_called_once()
                        mock_update_display.assert_called_once()
    
    def test_attempt_auto_login_failed_login(self):
        app = LibApp()
        
        with patch.object(app, 'get_saved_credentials') as mock_get_creds:
            mock_get_creds.return_value = ("saved_user", "saved_pass")
            
            with patch.object(app, '_handle_login_backend') as mock_login:
                mock_login.return_value = False
                
                with patch.object(app, 'showMainContainer') as mock_show:
                    with patch.object(app, 'update_user_info_display') as mock_update_display:
                        app.attempt_auto_login()
                        
                        mock_show.assert_called_once()
                        mock_update_display.assert_called_once()


class TestLibAppScreenMethods:
    
    def test_show_login_screen(self):
        app = LibApp()
        
        with patch('LibApp.LoginForm') as MockLoginForm:
            with patch('LibApp.ScreenPop') as MockScreenPop:
                mock_login_form = Mock()
                mock_screen_pop = Mock()
                
                MockLoginForm.return_value = mock_login_form
                MockScreenPop.return_value = mock_screen_pop
                
                with patch.object(app, 'hideMainContainer') as mock_hide:
                    with patch.object(app, 'push_screen') as mock_push:
                        app.show_login_screen()
                        
                        MockLoginForm.assert_called_once_with(
                            on_login=app._handle_login_backend,
                            on_register=app._handle_register_backend
                        )
                        
                        MockScreenPop.assert_called_once_with(
                            content_widget=mock_login_form,
                            on_close=app._on_login_close
                        )
                        
                        mock_hide.assert_called_once()
                        mock_push.assert_called_once_with(mock_screen_pop)
    
    def test_on_login_close(self):
        app = LibApp()
        app.current_user = "test_user"
        
        with patch.object(app, 'showMainContainer') as mock_show:
            with patch.object(app, '_update_library_keys_full') as mock_update:
                with patch.object(app, 'update_user_info_display') as mock_update_display:
                    app._on_login_close()
                    
                    mock_show.assert_called_once()
                    mock_update.assert_called_once()
                    mock_update_display.assert_called_once()
    
    def test_on_login_close_guest(self):
        app = LibApp()
        app.current_user = "Гость"
        
        with patch.object(app, 'showMainContainer') as mock_show:
            with patch.object(app, '_update_library_keys_full') as mock_update:
                with patch.object(app, 'update_user_info_display') as mock_update_display:
                    app._on_login_close()
                    
                    mock_show.assert_called_once()


class TestLibAppLibraryKeyMethods:
    
    def test_update_library_keys_full_success(self):
        app = LibApp()
        app.userid = "test_user"
        app.password = "test_pass"
        
        mock_response_data = {
            'success': True,
            'books': [
                {'key': 'key1', 'title': 'Book 1'},
                {'key': 'key2', 'title': 'Book 2'}
            ]
        }
        
        with patch('LibApp.requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response
            
            with patch.object(app, '_update_library_keys') as mock_update:
                with patch.object(app, 'update_user_info_display') as mock_update_display:
                    app._update_library_keys_full()
                    
                    expected_url = f"{app.base_url}/lib"
                    expected_data = {
                        "userid": "test_user",
                        "password": "test_pass",
                        "query": ""
                    }
                    mock_post.assert_called_once_with(expected_url, json=expected_data)
                    
                    mock_update.assert_called_once_with(mock_response_data['books'])
                    mock_update_display.assert_called_once()
    
    def test_update_library_keys_full_failure(self):
        app = LibApp()
        
        with patch('LibApp.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            
            app._update_library_keys_full()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

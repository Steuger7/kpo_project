import pytest
from unittest.mock import Mock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from booksContainer import BookContainer
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise


class TestBookContainerInitialization:
    
    def test_container_init_not_added(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        assert container.book == mock_book
        assert container.is_added is False
        assert container.can_focus is True
        assert container.focus_handler is None
        assert container.add_to_lib is mock_add
        assert container.rem_in_lib is mock_remove
    
    def test_container_init_added(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=True
        )
        
        assert container.book == mock_book
        assert container.is_added is True
        assert container.can_focus is True
        assert container.focus_handler is None
        assert container.add_to_lib is mock_add
        assert container.rem_in_lib is mock_remove
    
    def test_container_default_css(self):
        assert hasattr(BookContainer, 'DEFAULT_CSS')
        assert isinstance(BookContainer.DEFAULT_CSS, str)
        assert len(BookContainer.DEFAULT_CSS) > 0
        
        assert 'BookContainer' in BookContainer.DEFAULT_CSS
        assert '.book-title' in BookContainer.DEFAULT_CSS
        assert '.book-author' in BookContainer.DEFAULT_CSS
        assert '.book-year' in BookContainer.DEFAULT_CSS
        assert '.book-status_notAdded' in BookContainer.DEFAULT_CSS
        assert '.book-status_added' in BookContainer.DEFAULT_CSS


class TestBookContainerComposition:
    
    def test_compose_not_added(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        compose_result = container.compose()
        
        assert compose_result is not None
        
        assert container.is_added is False
    
    def test_compose_added(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=True
        )
        
        compose_result = container.compose()
        
        assert compose_result is not None
        
        assert container.is_added is True


class TestBookContainerFocusHandling:
    
    def test_set_focus_handler(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        handler = Mock()
        container.set_focus_handler(handler)
        
        assert container.focus_handler == handler
    
    def test_on_focus_with_handler(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        handler = Mock()
        container.set_focus_handler(handler)
        
        container.on_focus()
        
        handler.assert_called_once_with(container)
    
    def test_on_focus_without_handler(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        try:
            container.on_focus()
        except Exception as e:
            pytest.fail(f"on_focus() вызвал исключение: {e}")


class TestBookContainerKeyHandling:
    
    def test_on_key_enter_not_added_to_added(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        mock_status_widget = Mock()
        
        mock_event = Mock()
        mock_event.key = "enter"
        mock_event.stop = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            mock_query.return_value = mock_status_widget
            
            result = container.on_key(mock_event)
            
            assert result is False
            
            assert container.is_added is True
            
            mock_status_widget.update.assert_called_once_with("Статус: Добавлена в библиотеку")
            mock_status_widget.remove_class.assert_called_once_with("book-status_notAdded")
            mock_status_widget.add_class.assert_called_once_with("book-status_added")
            
            mock_add.assert_called_once_with(mock_book)
            mock_remove.assert_not_called()
            
            mock_event.stop.assert_called_once()
    
    def test_on_key_enter_added_to_not_added(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=True
        )
        
        mock_status_widget = Mock()
        
        mock_event = Mock()
        mock_event.key = "enter"
        mock_event.stop = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            mock_query.return_value = mock_status_widget
            
            result = container.on_key(mock_event)
            
            assert result is False
            
            assert container.is_added is False
            
            mock_status_widget.update.assert_called_once_with("Статус: Не добавлена")
            mock_status_widget.remove_class.assert_called_once_with("book-status_added")
            mock_status_widget.add_class.assert_called_once_with("book-status_notAdded")
            
            mock_remove.assert_called_once_with(mock_book)
            mock_add.assert_not_called()
            
            mock_event.stop.assert_called_once()
    
    def test_on_key_other_key(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        mock_event = Mock()
        mock_event.key = "space"
        mock_event.stop = Mock()
        
        result = container.on_key(mock_event)
        
        assert result is False
        
        mock_event.stop.assert_not_called()


class TestBookContainerSaveHandling:
    
    def test_handle_save_add_book(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        mock_status_widget = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            mock_query.return_value = mock_status_widget
            
            container._handle_save()
            
            assert container.is_added is True
            
            mock_status_widget.update.assert_called_once_with("Статус: Добавлена в библиотеку")
            mock_status_widget.remove_class.assert_called_once_with("book-status_notAdded")
            mock_status_widget.add_class.assert_called_once_with("book-status_added")
            
            mock_add.assert_called_once_with(mock_book)
            mock_remove.assert_not_called()
    
    def test_handle_save_remove_book(self):
        mock_book = {'title': 'Test', 'author': 'Author', 'year': '2023'}
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=mock_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=True
        )
        
        mock_status_widget = Mock()
        
        with patch.object(container, 'query_one') as mock_query:
            mock_query.return_value = mock_status_widget
            
            container._handle_save()
            
            assert container.is_added is False
            
            mock_status_widget.update.assert_called_once_with("Статус: Не добавлена")
            mock_status_widget.remove_class.assert_called_once_with("book-status_added")
            mock_status_widget.add_class.assert_called_once_with("book-status_notAdded")
            
            mock_remove.assert_called_once_with(mock_book)
            mock_add.assert_not_called()


class TestBookContainerEdgeCases:
    
    def test_empty_book_data(self):
        empty_book = {
            'title': '',
            'author': '',
            'year': ''
        }
        
        mock_add = Mock()
        mock_remove = Mock()
        
        container = BookContainer(
            book=empty_book,
            add_to_lib=mock_add,
            rem_in_lib=mock_remove,
            is_added=False
        )
        
        assert container.book == empty_book
        assert container.book['title'] == ''
        assert container.book['author'] == ''
        assert container.book['year'] == ''


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

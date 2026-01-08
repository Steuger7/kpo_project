import pytest
from unittest.mock import Mock, patch, PropertyMock, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from ScreenPop import ScreenPop
    from textual.screen import Screen
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise


class TestScreenPopInitialization:
    
    def test_screen_pop_init_basic(self):
        mock_widget = Mock()
        mock_widget.add_class = Mock()
        
        screen = ScreenPop(
            content_widget=mock_widget,
            on_close=None
        )
        
        assert screen.content_widget is mock_widget
        assert screen.on_close is None
        assert isinstance(screen, Screen)
    
    def test_screen_pop_init_with_on_close(self):
        mock_widget = Mock()
        mock_widget.add_class = Mock()
        mock_callback = Mock()
        
        screen = ScreenPop(
            content_widget=mock_widget,
            on_close=mock_callback
        )
        
        assert screen.content_widget is mock_widget
        assert screen.on_close is mock_callback


class TestScreenPopComposition:
    
    def test_compose_returns_correct_widget(self):
        mock_widget = Mock()
        mock_widget.add_class = Mock()
        
        screen = ScreenPop(
            content_widget=mock_widget,
            on_close=None
        )
        
        compose_result = list(screen.compose())
        
        assert compose_result == [mock_widget]


class TestScreenPopPopMethod:
    
    def test_pop_without_callback(self):
        mock_widget = Mock()
        mock_widget.add_class = Mock()
        
        screen = ScreenPop(
            content_widget=mock_widget,
            on_close=None
        )
        
        with patch.object(ScreenPop, 'app', new_callable=PropertyMock) as mock_app_prop:
            mock_app = Mock()
            mock_app.pop_screen = Mock()
            mock_app_prop.return_value = mock_app
            
            screen.pop()
            
            mock_app.pop_screen.assert_called_once()
    
    def test_pop_with_callback(self):
        mock_widget = Mock()
        mock_widget.add_class = Mock()
        mock_callback = Mock()
        
        screen = ScreenPop(
            content_widget=mock_widget,
            on_close=mock_callback
        )
        
        with patch.object(ScreenPop, 'app', new_callable=PropertyMock) as mock_app_prop:
            mock_app = Mock()
            mock_app.pop_screen = Mock()
            mock_app_prop.return_value = mock_app
            
            screen.pop()
            
            mock_callback.assert_called_once()
            
            mock_app.pop_screen.assert_called_once()


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

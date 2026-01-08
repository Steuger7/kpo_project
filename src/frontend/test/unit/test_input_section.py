import pytest
from unittest.mock import Mock, patch, PropertyMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from inputSection import InputSection
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    raise


class TestInputSectionComposition:
    
    def test_compose_creates_input(self):
        section = InputSection(
            section_title="Тест",
            input_placeholder="Введите текст"
        )
        
        compose_result = list(section.compose())
        
        assert len(compose_result) > 0
        
        assert compose_result[0] is not None
    
    def test_compose_with_correct_placeholder(self):
        section = InputSection(
            section_title="Тест",
            input_placeholder="Специальный плейсхолдер"
        )
        
        with patch('inputSection.Input') as MockInputClass:
            mock_input_instance = Mock()
            MockInputClass.return_value = mock_input_instance
            
            list(section.compose())
            
            MockInputClass.assert_called_once_with(
                placeholder="Специальный плейсхолдер",
                id="text-input",
                classes="text-input"
            )


class TestInputSectionEventHandling:
    
    def test_on_input_submitted_correct_input(self):
        callback = Mock()
        section = InputSection(
            section_title="Тест",
            input_placeholder="Введите текст",
            on_enter_callback=callback
        )
        
        mock_input = Mock()
        mock_input.id = "text-input"
        
        mock_event = Mock()
        mock_event.input = mock_input
        
        with patch.object(section, '_handle_submit') as mock_handle:
            section.on_input_submitted(mock_event)
            
            mock_handle.assert_called_once()
    
    def test_on_input_submitted_wrong_input(self):
        callback = Mock()
        section = InputSection(
            section_title="Тест",
            input_placeholder="Введите текст",
            on_enter_callback=callback
        )
        
        mock_input = Mock()
        mock_input.id = "wrong-input"  # Не тот ID
        
        mock_event = Mock()
        mock_event.input = mock_input
        
        with patch.object(section, '_handle_submit') as mock_handle:
            section.on_input_submitted(mock_event)
            
            mock_handle.assert_not_called()
    
    def test_on_input_submitted_without_callback(self):
        section = InputSection(
            section_title="Тест",
            input_placeholder="Введите текст"
        )
        
        mock_input = Mock()
        mock_input.id = "text-input"
        
        mock_event = Mock()
        mock_event.input = mock_input
        
        with patch.object(section, '_handle_submit') as mock_handle:
            section.on_input_submitted(mock_event)
            
            mock_handle.assert_called_once()


class TestInputSectionSubmitHandling:
    
    def test_handle_submit_with_text_and_callback(self):
        callback = Mock()
        section = InputSection(
            section_title="Тест",
            input_placeholder="Введите текст",
            on_enter_callback=callback
        )
        
        mock_input_widget = Mock()
        mock_input_widget.value = "  тестовый текст  "  # С пробелами
        mock_input_widget.focus_called = False
        
        def mock_focus():
            mock_input_widget.focus_called = True
        
        mock_input_widget.focus = mock_focus
        
        with patch.object(section, 'query_one') as mock_query:
            mock_query.return_value = mock_input_widget
            
            section._handle_submit()
            
            callback.assert_called_once_with("тестовый текст")
            
            assert mock_input_widget.value == ""
            
            assert mock_input_widget.focus_called is True
    
    def test_handle_submit_empty_text(self):
        callback = Mock()
        section = InputSection(
            section_title="Тест",
            input_placeholder="Введите текст",
            on_enter_callback=callback
        )
        
        mock_input_widget = Mock()
        mock_input_widget.value = "   "  # Только пробелы
        mock_input_widget.focus_called = False
        
        def mock_focus():
            mock_input_widget.focus_called = True
        
        mock_input_widget.focus = mock_focus
        
        with patch.object(section, 'query_one') as mock_query:
            mock_query.return_value = mock_input_widget
            
            section._handle_submit()
            
            callback.assert_called_once_with("")
            
            assert mock_input_widget.value == ""
            
            assert mock_input_widget.focus_called is True
  

if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))

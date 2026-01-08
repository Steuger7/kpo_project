
pytest . \
    --cov=LoginForm \
    --cov=booksContainer \
    --cov=inputSection \
    --cov=userContainer \
    --cov=ScreenPop \
    --cov=LibApp

find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

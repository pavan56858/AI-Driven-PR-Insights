# AI Code Review Assistant

A web application for analyzing pull requests with AI-powered code review capabilities. Built with HTML/CSS frontend and Flask (Python) backend.

## Features

- 📝 Submit pull requests for automated review
- 🔍 Static risk analysis
- 🤖 AI-powered code review
- 🔒 Security issue detection
- 📊 Review metrics dashboard
- 📈 Visual analytics with charts
- 🕐 Recent reviews tracking

## Project Structure

```
.
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML template with embedded CSS
└── README.md             # This file
```

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies:**

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install Flask==3.0.0 Werkzeug==3.0.1
```

## Running the Application

1. **Start the Flask server:**

```bash
python app.py
```

2. **Open your web browser and navigate to:**

```
http://localhost:5000
```

The application will be running on port 5000 by default.

## Usage

### Submitting a Pull Request for Review

1. Fill in the form fields:
   - **PR Title** (required): Title of your pull request
   - **Language**: Select the programming language
   - **Description**: Describe what the PR does
   - **Author**: PR author username
   - **Repository**: Repository name (format: org/repo)
   - **Source Branch**: Feature branch name
   - **Target Branch**: Target branch (e.g., main)
   - **Git Diff** (required): Paste your git diff content

2. Click "Load Sample PR" to populate the form with sample data

3. Click "Analyze Pull Request" to submit

### API Endpoints

The backend provides several REST API endpoints:

- `GET /` - Main application page
- `POST /analyze` - Analyze a pull request
- `GET /reviews` - Get all reviews
- `GET /reviews/<id>` - Get a specific review
- `GET /metrics` - Get review metrics

## Features Explained

### Static Risk Analysis
Analyzes code changes for potential risks and quality issues.

### AI-Powered Review
Provides intelligent feedback on code changes (placeholder implementation - can be extended with actual AI models).

### Security Detection
Detects potential security issues such as:
- Hardcoded passwords
- API keys or secrets in code
- Other security vulnerabilities

### Review Metrics Dashboard
Displays:
- Total reviews conducted
- Approved PRs
- PRs requiring changes
- Blocked PRs
- Weekly review chart

## Customization

### Extending the Analysis

The `perform_analysis()` function in `app.py` can be extended to include:
- Integration with actual AI/ML models
- More sophisticated security scanning
- Code quality metrics
- Complexity analysis
- Best practices checking

### Styling

All CSS is embedded in the HTML file (`templates/index.html`). You can modify colors, spacing, and layout by editing the `<style>` section.

## Development

### Adding New Features

1. **Backend**: Add new routes in `app.py`
2. **Frontend**: Modify `templates/index.html`
3. **Styling**: Update the CSS section in the HTML file

### Database Integration

For production use, replace the in-memory `reviews` list with a proper database:
- SQLite for simple applications
- PostgreSQL/MySQL for production
- MongoDB for document-based storage

Example using SQLite:

```python
import sqlite3

def init_db():
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
                 (id INTEGER PRIMARY KEY, pr_title TEXT, git_diff TEXT, ...)''')
    conn.commit()
    conn.close()
```

## Troubleshooting

### Port Already in Use

If port 5000 is already in use, modify the last line in `app.py`:

```python
app.run(debug=True, host='0.0.0.0', port=8000)  # Change to any available port
```

### Missing Dependencies

Make sure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

## Production Deployment

For production deployment:

1. **Set debug to False:**
```python
app.run(debug=False)
```

2. **Use a production WSGI server:**
```bash
pip install gunicorn
gunicorn app:app
```

3. **Set up environment variables for sensitive data**

4. **Use a proper database instead of in-memory storage**

5. **Add authentication and authorization**

6. **Implement rate limiting**

7. **Set up HTTPS**

## License

This project is provided as-is for educational and development purposes.

## Support

For issues or questions, please refer to the Flask documentation: https://flask.palletsprojects.com/

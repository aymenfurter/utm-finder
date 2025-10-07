# UTM Finder

A Python web application that analyzes arXiv papers to find links containing `utm_source=chatgpt.com` parameters. This tool helps track the growing trend of ChatGPT references in academic papers since 2023.

## Features

- 🔍 Automatically downloads and analyzes arXiv papers
- 📊 Extracts and identifies URLs with ChatGPT UTM parameters
- 📈 Visualizes trends over time with interactive charts
- 🎨 Modern, responsive web interface
- 📄 Displays detailed information about papers containing ChatGPT links

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aymenfurter/utm-finder.git
cd utm-finder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the web application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Click the "Start Analysis" button to begin analyzing arXiv papers

4. View the results, statistics, and trends on the dashboard

## How it Works

1. **Paper Collection**: Fetches recent papers from arXiv in CS categories (AI, CL, LG)
2. **PDF Analysis**: Downloads PDFs and extracts all URLs from text and annotations
3. **UTM Detection**: Identifies links containing `utm_source=chatgpt.com`
4. **Statistics**: Aggregates data by year and month to show trends
5. **Visualization**: Displays results with interactive charts and detailed paper information

## API Endpoints

- `GET /` - Main web interface
- `POST /api/analyze` - Trigger analysis of arXiv papers
- `GET /api/results` - Get cached analysis results

## Example Usage

Run the example script to test the UTM detection:
```bash
python example.py
```

## Configuration

The application analyzes papers from 2023 onwards by default. You can modify the following in `app.py`:
- `max_results`: Number of papers to analyze (default: 100)
- `start_date`: Starting date for analysis (default: 2023-01-01)
- Search categories: Currently set to CS.AI, CS.CL, CS.LG

## Requirements

- Python 3.8+
- Flask 3.0.0
- PyPDF2 3.0.1
- requests 2.31.0
- arxiv 2.1.0
- python-dateutil 2.8.2

## License

MIT License
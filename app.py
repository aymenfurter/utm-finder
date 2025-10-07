#!/usr/bin/env python3
"""
UTM Finder - A webapp to analyze arXiv PDFs for ChatGPT UTM parameters
"""

import os
import re
import tempfile
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, jsonify
import arxiv
import requests
import PyPDF2
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Store results in memory
results_cache = {
    'papers': [],
    'stats': {},
    'last_updated': None
}

def extract_links_from_pdf(pdf_path):
    """Extract all URLs from a PDF file."""
    links = []
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                # Find URLs in the text
                url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
                found_urls = re.findall(url_pattern, text)
                links.extend(found_urls)
                
                # Also check annotations
                if '/Annots' in page:
                    annotations = page['/Annots']
                    for annotation in annotations:
                        obj = annotation.get_object()
                        if '/A' in obj and '/URI' in obj['/A']:
                            uri = obj['/A']['/URI']
                            if isinstance(uri, str):
                                links.append(uri)
    except Exception as e:
        print(f"Error extracting links from PDF: {e}")
    
    return links

def check_utm_source(url, source='chatgpt.com'):
    """Check if URL contains utm_source parameter with specified value."""
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        utm_source = params.get('utm_source', [])
        return source in utm_source
    except:
        return False

def download_pdf(paper_id):
    """Download a paper from arXiv."""
    try:
        paper = next(arxiv.Search(id_list=[paper_id]).results())
        pdf_url = paper.pdf_url
        
        response = requests.get(pdf_url, timeout=30)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(response.content)
                return tmp_file.name
    except Exception as e:
        print(f"Error downloading paper {paper_id}: {e}")
    return None

def analyze_arxiv_papers(max_results=50, start_date=None):
    """Analyze recent arXiv papers for ChatGPT UTM parameters."""
    results = []
    
    # Search arXiv for recent papers
    # Focus on CS (Computer Science) papers
    search_query = "cat:cs.AI OR cat:cs.CL OR cat:cs.LG"
    
    if start_date:
        # Limit to papers after start_date
        search_query += f" AND submittedDate:[{start_date.strftime('%Y%m%d')}0000 TO *]"
    
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )
    
    for paper in search.results():
        paper_id = paper.entry_id.split('/')[-1]
        print(f"Processing paper: {paper_id} - {paper.title}")
        
        # Download and analyze PDF
        pdf_path = download_pdf(paper_id)
        if pdf_path:
            links = extract_links_from_pdf(pdf_path)
            chatgpt_links = [link for link in links if check_utm_source(link)]
            
            if chatgpt_links:
                results.append({
                    'id': paper_id,
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'published': paper.published.isoformat(),
                    'chatgpt_links': chatgpt_links,
                    'total_links': len(links)
                })
            
            # Clean up temp file
            os.unlink(pdf_path)
    
    return results

def calculate_stats(papers):
    """Calculate statistics from analyzed papers."""
    stats = {
        'total_papers_analyzed': 0,
        'papers_with_chatgpt_utm': len(papers),
        'total_chatgpt_links': sum(len(p['chatgpt_links']) for p in papers),
        'by_year': defaultdict(int),
        'by_month': defaultdict(int)
    }
    
    for paper in papers:
        published_date = datetime.fromisoformat(paper['published'])
        year = published_date.year
        month = f"{year}-{published_date.month:02d}"
        
        stats['by_year'][str(year)] += 1
        stats['by_month'][month] += 1
    
    # Convert defaultdicts to regular dicts and sort
    stats['by_year'] = dict(sorted(stats['by_year'].items()))
    stats['by_month'] = dict(sorted(stats['by_month'].items()))
    
    return stats

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Trigger analysis of arXiv papers."""
    try:
        # Analyze papers from 2023 onwards
        start_date = datetime(2023, 1, 1)
        papers = analyze_arxiv_papers(max_results=100, start_date=start_date)
        
        # Calculate statistics
        stats = calculate_stats(papers)
        
        # Update cache
        results_cache['papers'] = papers
        results_cache['stats'] = stats
        results_cache['last_updated'] = datetime.now().isoformat()
        
        return jsonify({
            'success': True,
            'papers_found': len(papers),
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/results')
def get_results():
    """Get the current analysis results."""
    return jsonify(results_cache)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

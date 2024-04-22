from flask import Flask, render_template, request, redirect, url_for, jsonify
from urllib.parse import urlparse
import subprocess
import json
import os

app = Flask(__name__)

# Function to read crawled URLs from the file and return them as a list
def get_crawled_urls():
    crawled_urls = []
    with open('asyncapp.csv', 'r') as f:
        for line in f:
            crawled_urls.append(line.strip())
    return crawled_urls

# Function to clear the contents of the .csv file
def clear_crawled_urls():
    open('asyncapp.csv', 'w').close()

@app.route('/')
def index():
    # Get the list of crawled URLs
    crawled_urls = get_crawled_urls()
    return render_template('index.html', crawled_urls=crawled_urls)

@app.route('/update_config', methods=['POST'])
def update_config():
    urltocrawl = request.form.get('urltocrawl')
    with open('config.json', 'r+') as f:
        config = json.load(f)
        config['urltocrawl'] = urltocrawl
        f.seek(0)
        json.dump(config, f, indent=4)
        f.truncate()
    # Execute the Node.js script
    subprocess.run(["npm", "run", "asyncapp"])
    # Redirect to the home page to display the crawled URLs
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear():
    # Clear the contents of the .csv file
    clear_crawled_urls()
    # Redirect to the home page
    return redirect(url_for('index'))

@app.route('/whitelisted_urls', methods=['GET', 'POST'])
def whitelisted_urls():
    if request.method == 'POST':
        whitelisted_urls = request.form.getlist('whitelisted_url')
        whitelisted_urls.append("URL")
        
        whitelisted_domains = [urlparse(url).netloc for url in whitelisted_urls]
        crawled_urls = get_crawled_urls()

        failed_urls = [url for url in crawled_urls if not any(urlparse(url).netloc == domain for domain in whitelisted_domains)]

        if not failed_urls:
            result = "Operation success"
        else:
            result = "Patient failure because of: {}".format(failed_urls)
        
        return jsonify(result=result)
    
    return render_template('whitelisted_urls.html')





if __name__ == '__main__':
    app.run(debug=True)

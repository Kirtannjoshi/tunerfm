import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_stream_url_from_station_page(page_url):
    try:
        response = requests.get(page_url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for <audio> tags
        audio_source = soup.find('audio')
        if audio_source and audio_source.get('src'):
            return audio_source['src']

        # Look for common stream file extensions in script tags or link tags
        # This is a more generic approach, might need refinement
        for script in soup.find_all('script'):
            if script.string:
                match = re.search(r'(https?://[^\s"\\]+\.(?:mp3|aac|m3u|pls|m4a|ogg))', script.string)

                if match:
                    return match.group(1)
        
        # Look for links with common stream file extensions
        for link in soup.find_all('a', href=True):
            if re.search(r'\.(?:mp3|aac|m3u|pls|m4a|ogg)$', link['href']):
                return link['href']

        # More specific search for common player configurations (e.g., jwplayer, video.js)
        # This often involves looking for JSON or JS object literals containing 'file' or 'src'
        # Example: var playerInstance = jwplayer("myElement").setup({ file: "http://stream.url/" });
        for script in soup.find_all('script'):
            if script.string:
                # Attempt to find patterns like 'file: "stream_url"' or 'src: "stream_url"'
                match = re.search(r'(file|src)\s*:\s*["\\](https?://[^\s"\\]+\.(?:mp3|aac|m3u|pls|m4a|ogg))["\\]', script.string)
                if match:
                    return match.group(2)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {page_url}: {e}")
    return None

def scrape_onlineradiofm():
    stations_list_url = "https://onlineradiofm.in/stations"
    response = requests.get(stations_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    stations = []
    # The structure seems to be a div containing the station name, country, and frequency.
    # We need to find a way to identify these blocks and then extract the information.
    # Based on the web search result, it looks like each station is a direct text block.
    # We'll look for a common parent or pattern.
    # Let's assume stations are within a container, and we can iterate through them.
    # A common pattern might be a div with a specific class, or just iterating through children of a main content div.
    
    # This is a heuristic. We'll try to find all <div> elements that contain 'Country:'
    # and then parse the text content to extract name, country, and try to infer stream/logo.
    # This site might not expose stream URLs directly in the HTML of the listing page.
    # If not, a more advanced approach (e.g., Selenium to interact with play buttons) would be needed.
    
    # For now, let's try to extract what's visible and make educated guesses for stream URLs.
    # This part is highly dependent on the actual HTML structure of onlineradiofm.in/stations
    
    # Example: Find all divs that contain 'Country:'
    station_blocks = soup.find_all(lambda tag: tag.name == 'div' and 'Country:' in tag.get_text())

    for block in station_blocks:
        text_content = block.get_text(separator=' ', strip=True)
        lines = [line.strip() for line in text_content.split('\n') if line.strip()]
        
        name = "Unknown Name"
        country = "Unknown Country"
        frequency = "Unknown Frequency"
        station_page_url = None
        
        if lines:
            name = lines[0] # Assuming the first line is the name
            for line in lines[1:]:
                if "Country:" in line: country = line.replace("Country:", "").strip()
                if "Frequency:" in line: frequency = line.replace("Frequency:", "").strip()
        
        # Try to find the link to the station's individual page within the block
        link_tag = block.find('a', href=True)
        if link_tag:
            station_page_url = link_tag['href']
            # Ensure it's an absolute URL
            if not station_page_url.startswith('http'):
                station_page_url = "https://onlineradiofm.in" + station_page_url

        stream_url = "https://example.com/stream_placeholder"
        logo = '/static/default-radio.png'
        playable = False

        if station_page_url:
            print(f"Attempting to get stream URL for {name} from {station_page_url}")
            found_stream = get_stream_url_from_station_page(station_page_url)
            if found_stream:
                stream_url = found_stream
                playable = True
                print(f"Found stream for {name}: {stream_url}")
            else:
                print(f"No stream found for {name} on {station_page_url}")

        stations.append({
            'name': name,
            'genre': "Unknown",
            'country': country,
            'language': "Unknown",
        })
        print(f"Scraped station: {name}, Country: {country}")
    
    print(f"Scraped {len(stations)} stations from onlineradiofm.in. Note: Stream URLs and logos are placeholders.")
    return stations

def get_radio_browser_stations():
    api_url = "https://de1.api.radio-browser.info/json/stations/search?limit=100&hidebroken=true"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        stations = []
        for item in data:
            stations.append({
                'name': item.get('name', 'Unknown Name'),
                'genre': item.get('tags', 'Unknown Genre'),
                'country': item.get('country', 'Unknown Country'),
                'language': item.get('language', 'Unknown Language'),
                'logo': item.get('favicon', '/static/default-radio.png'),
                'stream': item.get('url_resolved', item.get('url', '')),
                'playable': True # Assume radio-browser.info streams are playable
            })
        print(f"Fetched {len(stations)} stations from radio-browser.info.")
        return stations
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from radio-browser.info API: {e}")
        return []
    # This is a placeholder. You'll need to use the radio-browser.info API.
    # Refer to https://www.radio-browser.info/ for API documentation.
    # Example:
    # api_url = "https://de1.api.radio-browser.info/json/stations/search?limit=100"
    # response = requests.get(api_url)
    # return response.json()
    print("Integration with radio-browser.info API needs to be implemented.")
    return []



def main():
    all_stations = []

    # Scrape from onlineradiofm.in
    onlineradiofm_stations = scrape_onlineradiofm()
    all_stations.extend(onlineradiofm_stations)

    # Integrate with radio-browser.info
    radio_browser_stations = get_radio_browser_stations()
    all_stations.extend(radio_browser_stations)

    # Add hardcoded open-source streams
    hardcoded_stations = [
        {
            "name": "Radio Paradise",
            "genre": "Eclectic",
            "country": "USA",
            "language": "English",
            "logo": "/static/default-radio.png",
            "stream": "http://stream-uk1.radioparadise.com/aac-320",
            "playable": True
        },
        {
            "name": "SomaFM Groove Salad",
            "genre": "Downtempo",
            "country": "USA",
            "language": "English",
            "logo": "/static/default-radio.png",
            "stream": "https://ice5.somafm.com/groovesalad-128-mp3",
            "playable": True
        },
        {
            "name": "Sai Global Harmony",
            "genre": "Spiritual",
            "country": "India",
            "language": "English",
            "logo": "/static/default-radio.png",
            "stream": "https://stream-ssl.radiosai.net:8004/",
            "playable": True
        }
    ]
    all_stations.extend(hardcoded_stations)

    # Save to JSON file
    with open('radio_stations.json', 'w', encoding='utf-8') as f:
        json.dump(all_stations, f, ensure_ascii=False, indent=4)
    print(f"Scraped and combined {len(all_stations)} stations into radio_stations.json")



def get_radio_browser_stations():
    api_url = "https://de1.api.radio-browser.info/json/stations/search?limit=100&hidebroken=true"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        
        stations = []
        for item in data:
            stations.append({
                'name': item.get('name', 'Unknown Name'),
                'genre': item.get('tags', 'Unknown Genre'),
                'country': item.get('country', 'Unknown Country'),
                'language': item.get('language', 'Unknown Language'),
                'logo': item.get('favicon', '/static/default-radio.png'),
                'stream': item.get('url_resolved', item.get('url', '')),
                'playable': True # Assume radio-browser.info streams are playable
            })
        print(f"Fetched {len(stations)} stations from radio-browser.info.")
        return stations
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from radio-browser.info API: {e}")
        return []
    # This is a placeholder. You'll need to use the radio-browser.info API.
    # Refer to https://www.radio-browser.info/ for API documentation.
    # Example:
    # api_url = "https://de1.api.radio-browser.info/json/stations/search?limit=100"
    # response = requests.get(api_url)
    # return response.json()
    print("Integration with radio-browser.info API needs to be implemented.")
    return []



def main():
    all_stations = []

    # Scrape from onlineradiofm.in
    onlineradiofm_stations = scrape_onlineradiofm()
    all_stations.extend(onlineradiofm_stations)

    # Integrate with radio-browser.info
    radio_browser_stations = get_radio_browser_stations()
    all_stations.extend(radio_browser_stations)

    # Add hardcoded open-source streams
    hardcoded_stations = [
        {
            "name": "Radio Paradise",
            "genre": "Eclectic",
            "country": "USA",
            "language": "English",
            "logo": "/static/default-radio.png",
            "stream": "http://stream-uk1.radioparadise.com/aac-320",
            "playable": True
        },
        {
            "name": "SomaFM Groove Salad",
            "genre": "Downtempo",
            "country": "USA",
            "language": "English",
            "logo": "/static/default-radio.png",
            "stream": "https://ice5.somafm.com/groovesalad-128-mp3",
            "playable": True
        },
        {
            "name": "Sai Global Harmony",
            "genre": "Spiritual",
            "country": "India",
            "language": "English",
            "logo": "/static/default-radio.png",
            "stream": "https://stream-ssl.radiosai.net:8004/",
            "playable": True
        }
    ]
    all_stations.extend(hardcoded_stations)

    # Save to JSON file
    with open('radio_stations.json', 'w', encoding='utf-8') as f:
        json.dump(all_stations, f, ensure_ascii=False, indent=4)
    print(f"Scraped and combined {len(all_stations)} stations into radio_stations.json")

if __name__ == "__main__":
    main()
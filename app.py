import requests
import json
from flask import Flask, render_template, request

# --- INITIALIZE FLASK APPLICATION ---
app = Flask(__name__)

# --- API CALL FUNCTIONS (unchanged from the previous script) ---
BASE_HEADERS = {
    "accept": "application/json", "accept-language": "en", "clientid": "OIEwebsite",
    "content-type": "application/json", "env": "PRD", "token": "#PIPRD202006#",
    "type": "REQUEST", "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Microsoft Edge\";v=\"140\"",
    "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "Referer": "https://wahis.woah.org/"
}

def get_all_countries():
    url = "https://wahis.woah.org/api/v1/pi/country/list?language=en"
    try:
        response = requests.get(url, headers=BASE_HEADERS)
        response.raise_for_status()
        # Sort the list of countries by name for easier lookup
        return sorted(response.json(), key=lambda x: x['name'])
    except Exception as e:
        print(f"Critical error while fetching country list: {e}")
        return []

def get_all_diseases():
    url = "https://wahis.woah.org/api/v1/pi/disease/first-level-filters?language=en"
    try:
        response = requests.get(url, headers=BASE_HEADERS)
        response.raise_for_status()
        # Sort the list of diseases by name
        return sorted(response.json(), key=lambda x: x['name'])
    except Exception as e:
        print(f"Critical error while fetching disease list: {e}")
        return []

def get_filtered_events(country_id: int, disease_id: int):
    url = "https://wahis.woah.org/api/v1/pi/event/filtered-list"
    body = {
        "eventIds": [], "reportIds": [], "countries": [country_id],
        "firstDiseases": [disease_id], "secondDiseases": [], "typeStatuses": [],
        "reasons": [], "eventStatuses": [], "reportTypes": [], "reportStatuses": [],
        "eventStartDate": None, "submissionDate": None, "animalTypes": [],
        "sortColumn": "submissionDate", "sortOrder": "desc", "pageSize": 10, "pageNumber": 0
    }
    
    # --- DEBUG SECTION ADDED ---
    print("\n" + "="*50)
    print("--- Sending request to API filtered-list ---")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(BASE_HEADERS, indent=2)}")
    print(f"Body (JSON format): {json.dumps(body)}")
    
    try:
        response = requests.post(url, headers=BASE_HEADERS, data=json.dumps(body), timeout=15) # Added timeout
        
        # Print response details regardless of success or failure
        print("\n--- Response received from WAHIS server ---")
        print(f"Status Code: {response.status_code}")
        
        # Attempt to print the response content as text, fallback to raw content if it fails
        try:
            print(f"Response Content (Text): {response.text}")
        except Exception as e:
            print(f"Unable to read text content, printing raw bytes: {response.content}")
        
        print("="*50 + "\n")

        # Check if the request was successful (status code 2xx)
        response.raise_for_status()
        
        # If successful, return the JSON data
        return response.json()

    except requests.exceptions.HTTPError as http_err:
        print(f"!!! Specific HTTP error: {http_err}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"!!! Connection or timeout error: {e}")
        return None
    except json.JSONDecodeError:
        print("!!! Error: Response is not valid JSON. The website might be under maintenance or blocking requests.")
        return None

# --- DATA CACHE ---
# Load data once when the server starts to improve performance
print("Starting server, please wait while data is being fetched from WAHIS...")
COUNTRIES_CACHE = get_all_countries()
DISEASES_CACHE = get_all_diseases()
if COUNTRIES_CACHE and DISEASES_CACHE:
    print("Data successfully loaded. Server is ready!")
else:
    print("WARNING: Unable to fetch data from WAHIS. The application may not function correctly.")

# --- DEFINE ROUTES FOR THE WEB PAGE ---
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    selected_country = None
    selected_disease = None
    
    # If the user submits the form (clicks the search button)
    if request.method == 'POST':
        try:
            # Get IDs from the user's form selection
            country_id = int(request.form.get('country'))
            disease_id = int(request.form.get('disease'))
            
            # Save the selection to display it back in the dropdown
            selected_country = country_id
            selected_disease = disease_id
            
            print(f"Search request received - Country ID: {country_id}, Disease ID: {disease_id}")
            # Call the API to fetch results
            results = get_filtered_events(country_id, disease_id)
        except (TypeError, ValueError):
             # Handle cases where the user submits without selecting anything
            print("Error: User did not select sufficient information.")
            pass # Ignore and just reload the page

    # Render the web page, passing necessary data to the HTML template
    return render_template('index.html', 
                           countries=COUNTRIES_CACHE, 
                           diseases=DISEASES_CACHE,
                           results=results,
                           selected_country=selected_country,
                           selected_disease=selected_disease)

# --- RUN THE APPLICATION ---
if __name__ == '__main__':
    # debug=True enables auto-reloading when you make changes to the code
    app.run(debug=True, host='0.0.0.0', port=5001) 
import requests
import json
from flask import Flask, render_template, request

app = Flask(__name__)

BASE_HEADERS = {
    "accept": "application/json", "accept-language": "en", "clientid": "OIEwebsite",
    "content-type": "application/json", "env": "PRD", "token": "#PIPRD202006#",
    "type": "REQUEST",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Referer": "https://wahis.woah.org/"
}

# --- CÁC HÀM TẢI DỮ LIỆU BAN ĐẦU (Không thay đổi) ---
def load_initial_data():
    countries, diseases = [], []
    print("Attempting to load countries data...")
    try:
        url = "https://wahis.woah.org/api/v1/pi/country/list?language=en"
        response = requests.get(url, headers=BASE_HEADERS, timeout=15)
        response.raise_for_status()
        countries = sorted(response.json(), key=lambda x: x['name'])
        print("Successfully loaded countries data.")
    except Exception as e:
        print(f"!!! CRITICAL ERROR loading countries: {e}")
    print("Attempting to load diseases data...")
    try:
        url = "https://wahis.woah.org/api/v1/pi/disease/first-level-filters?language=en"
        response = requests.get(url, headers=BASE_HEADERS, timeout=15)
        response.raise_for_status()
        diseases = sorted(response.json(), key=lambda x: x['name'])
        print("Successfully loaded diseases data.")
    except Exception as e:
        print(f"!!! CRITICAL ERROR loading diseases: {e}")
    return countries, diseases

print("Server is starting, loading initial data from WAHIS...")
COUNTRIES_CACHE, DISEASES_CACHE = load_initial_data()
if COUNTRIES_CACHE and DISEASES_CACHE:
    print("Initial data loaded successfully. Server is ready!")
else:
    print("WARNING: Failed to load some or all initial data.")

# --- THAY ĐỔI 1: LÀM CHO HÀM `get_filtered_events` LINH HOẠT HƠN ---
def get_filtered_events(country_id=None, disease_id=None):
    """
    Hàm này giờ có thể nhận ID hoặc không.
    Nếu không có ID, nó sẽ tìm kiếm cho 'Tất cả'.
    """
    url = "https://wahis.woah.org/api/v1/pi/event/filtered-list"
    
    # Nếu country_id được cung cấp, thêm nó vào body. Nếu không, gửi một danh sách rỗng (nghĩa là 'Tất cả')
    countries_filter = [country_id] if country_id else []
    diseases_filter = [disease_id] if disease_id else []
    
    body = {
        "countries": countries_filter,
        "firstDiseases": diseases_filter,
        "eventIds": [], "reportIds": [], "secondDiseases": [], "typeStatuses": [],
        "reasons": [], "eventStatuses": [], "reportTypes": [], "reportStatuses": [],
        "eventStartDate": None, "submissionDate": None, "animalTypes": [],
        "sortColumn": "submissionDate", "sortOrder": "desc", "pageSize": 10, "pageNumber": 0
    }
    try:
        response = requests.post(url, headers=BASE_HEADERS, data=json.dumps(body), timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error when fetching filtered events: {e}")
        return None

# --- THAY ĐỔI 2: CẬP NHẬT LOGIC CỦA ROUTE `index` ---
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    selected_country = "all"  # Mặc định là 'all'
    selected_disease = "all"  # Mặc định là 'all'
    
    if request.method == 'POST':
        # Lấy lựa chọn của người dùng từ form
        country_id_str = request.form.get('country')
        disease_id_str = request.form.get('disease')

        # Cập nhật lại lựa chọn để hiển thị trên dropdown
        selected_country = country_id_str
        selected_disease = disease_id_str
        
        # Chuyển đổi giá trị từ form sang dạng số hoặc None
        # Nếu người dùng chọn 'all', giá trị sẽ là None
        country_id = int(country_id_str) if country_id_str != 'all' else None
        disease_id = int(disease_id_str) if disease_id_str != 'all' else None
        
        print(f"Search request received - Country: {country_id_str}, Disease: {disease_id_str}")
        results = get_filtered_events(country_id, disease_id)
    else:
        # Đây là yêu cầu GET (lần đầu tải trang)
        # Tự động tìm kiếm các sự kiện mới nhất trên toàn thế giới
        print("Initial page load. Fetching latest events for all countries/diseases.")
        results = get_filtered_events() # Gọi hàm không có tham số

    return render_template('index.html', 
                           countries=COUNTRIES_CACHE, 
                           diseases=DISEASES_CACHE,
                           results=results,
                           selected_country=selected_country,
                           selected_disease=selected_disease)

if __name__ == '__main__':
    app.run(debug=True)
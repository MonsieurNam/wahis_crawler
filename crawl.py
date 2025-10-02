import requests
import json
from typing import List, Dict, Optional

# Các headers cơ bản, không thay đổi
BASE_HEADERS = {
    "accept": "application/json", "accept-language": "en", "clientid": "OIEwebsite",
    "content-type": "application/json", "env": "PRD", "token": "#PIPRD202006#",
    "type": "REQUEST", "sec-ch-ua": "\"Chromium\";v=\"140\", \"Not=A?Brand\";v=\"24\", \"Microsoft Edge\";v=\"140\"",
    "sec-ch-ua-mobile": "?0", "sec-ch-ua-platform": "\"Windows\"", "Referer": "https://wahis.woah.org/"
}

def get_all_countries() -> Optional[List[Dict]]:
    """Lấy danh sách tất cả quốc gia và ID của chúng từ API."""
    url = "https://wahis.woah.org/api/v1/pi/country/list?language=en"
    try:
        response = requests.get(url, headers=BASE_HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy danh sách quốc gia: {e}")
        return None

def get_all_diseases() -> Optional[List[Dict]]:
    """Lấy danh sách tất cả bệnh và ID của chúng từ API."""
    url = "https://wahis.woah.org/api/v1/pi/disease/first-level-filters?language=en"
    try:
        response = requests.get(url, headers=BASE_HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy danh sách bệnh: {e}")
        return None

# --- HÀM ĐÃ SỬA LỖI HOÀN CHỈNH ---
def find_id_by_name(name: str, item_list: List[Dict], name_key: str, id_key: str) -> Optional[int]:
    """
    Tìm ID dựa trên tên trong một danh sách, sử dụng các key được chỉ định.
    Hàm này có thể xử lý cả cấu trúc dữ liệu của quốc gia và bệnh.
    """
    search_name = name.lower().strip()
    
    # Ưu tiên tìm kiếm khớp chính xác
    for item in item_list:
        if isinstance(item, dict) and name_key in item and item[name_key]:
            if search_name == item[name_key].lower().strip():
                if id_key in item:
                    # Xử lý trường hợp ID nằm trong list (cho bệnh)
                    if id_key == 'ids' and isinstance(item[id_key], list) and item[id_key]:
                        return item[id_key][0]
                    # Xử lý trường hợp ID là giá trị trực tiếp (cho quốc gia)
                    else:
                        return item[id_key]
    
    # Nếu không thấy, thử tìm kiếm chứa chuỗi (linh hoạt hơn)
    for item in item_list:
        if isinstance(item, dict) and name_key in item and item[name_key]:
            if search_name in item[name_key].lower().strip():
                print(f"(Có phải bạn muốn tìm: '{item[name_key]}'?)")
                if id_key in item:
                    if id_key == 'ids' and isinstance(item[id_key], list) and item[id_key]:
                        return item[id_key][0]
                    else:
                        return item[id_key]
    return None

def get_filtered_events(country_id: int, disease_id: int):
    """Lấy và lọc các sự kiện dịch bệnh động vật từ API của WOAH sử dụng ID."""
    url = "https://wahis.woah.org/api/v1/pi/event/filtered-list"
    body = {
        "eventIds": [], "reportIds": [], "countries": [country_id],
        "firstDiseases": [disease_id], "secondDiseases": [], "typeStatuses": [],
        "reasons": [], "eventStatuses": [], "reportTypes": [], "reportStatuses": [],
        "eventStartDate": None, "submissionDate": None, "animalTypes": [],
        "sortColumn": "submissionDate", "sortOrder": "desc", "pageSize": 10, "pageNumber": 0
    }
    try:
        response = requests.post(url, headers=BASE_HEADERS, data=json.dumps(body))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"Lỗi HTTP xảy ra: {http_err} - Phản hồi từ máy chủ: {response.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Đã xảy ra lỗi kết nối: {e}")
        return None

if __name__ == "__main__":
    print("Đang tải danh sách quốc gia và bệnh từ WAHIS...")
    countries = get_all_countries()
    diseases = get_all_diseases()

    if not countries or not diseases:
        print("Không thể tải dữ liệu cần thiết. Vui lòng thử lại sau.")
    else:
        print("Tải thành công!")
        while True:
            input_country_name = input("\nNhập tên quốc gia (hoặc gõ 'exit' để thoát): ")
            if input_country_name.lower() == 'exit':
                break
            
            # --- GỌI HÀM VỚI ĐÚNG KEY ---
            country_id = find_id_by_name(input_country_name, countries, name_key='name', id_key='areaId')

            if country_id is None:
                print(f"Không tìm thấy quốc gia nào có tên là '{input_country_name}'. Vui lòng thử lại.")
                continue

            input_disease_name = input("Nhập tên bệnh: ")
            # --- GỌI HÀM VỚI ĐÚNG KEY ---
            disease_id = find_id_by_name(input_disease_name, diseases, name_key='name', id_key='ids')

            if disease_id is None:
                print(f"Không tìm thấy bệnh nào có tên là '{input_disease_name}'. Vui lòng thử lại.")
                continue

            print(f"\nĐang tìm kiếm sự kiện cho quốc gia ID: {country_id} và bệnh ID: {disease_id}...")
            filtered_events = get_filtered_events(country_id, disease_id)

            # Kiểm tra xem có dữ liệu trả về không
            if filtered_events and filtered_events.get('data'):
                print("\nKết quả đã lọc:")
                print(json.dumps(filtered_events, indent=4, ensure_ascii=False))
            else:
                print("Không tìm thấy sự kiện nào phù hợp với tiêu chí.")
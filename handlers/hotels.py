import os
import requests
import json
from dotenv import load_dotenv


load_dotenv()

class GooglePlacesHotelFinder:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_PLACES_API_KEY')

    def geocode_address(self, address):
        endpoint = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params)
            results = response.json()
            
            if results['status'] == 'OK':
                location = results['results'][0]['geometry']['location']
                return f"{location['lat']},{location['lng']}"
            else:
                print(f"Ошибка геокодирования: {results['status']} - {results.get('error_message', '')}")
                return None
        except Exception as e:
            print(f"Ошибка при геокодировании: {str(e)}")
            return None

    def find_nearby_hotels(self, location, radius=5000, max_results=20):
        if not (isinstance(location, str) and ',' in location and 
                all(s.strip().replace('.', '').isdigit() for s in location.split(','))):
            print(f"Преобразуем адрес в координаты: {location}")
            location = self.geocode_address(location)
            if not location:
                return None
        
        endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        
        params = {
            'location': location,
            'radius': radius,
            'type': 'lodging',
            'key': self.api_key,
            'language': 'ru'
        }

        try:
            hotels = []
            next_page_token = None
            
            while len(hotels) < max_results:
                if next_page_token:
                    params['pagetoken'] = next_page_token
                    import time
                    time.sleep(2)
                
                response = requests.get(endpoint_url, params=params)
                results = response.json()
                
                if results['status'] == 'OK':
                    for place in results['results']:
                        hotel = {
                            'name': place.get('name'),
                            'address': place.get('vicinity'),
                            'rating': place.get('rating'),
                            'price_level': place.get('price_level'),
                            'location': place.get('geometry', {}).get('location'),
                            'place_id': place.get('place_id')
                        }
                        hotels.append(hotel)
                        
                        if len(hotels) >= max_results:
                            break
                    
                    next_page_token = results.get('next_page_token')
                    if not next_page_token:
                        break
                else:
                    print(f"Ошибка при запросе: {results['status']} - {results.get('error_message', '')}")
                    break
            
            return hotels[:max_results]
            
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
            return None

    def print_hotels(self, hotels):
        if not hotels:
            print("Отели не найдены")
            return
        
        print(f"\nНайдено отелей: {len(hotels)}")
        for i, hotel in enumerate(hotels, 1):
            print(f"\n{i}. {hotel['name']}")
            print(f"   Адрес: {hotel['address']}")
            print(f"   Рейтинг: {hotel.get('rating', 'нет данных')}")
            print(f"   Уровень цен: {'$' * hotel.get('price_level', 0) if hotel.get('price_level') else 'нет данных'}")
            print(f"   Координаты: {hotel['location']}")



if __name__ == "__main__":
    try:
        finder = GooglePlacesHotelFinder()
        place = input('Название улицы: ')
        hotels = finder.find_nearby_hotels(place, radius=2000, max_results=10)
        finder.print_hotels(hotels)
        
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
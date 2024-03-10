# import requests
#
# # Define location
# location = f"{country}, {city}"
#
# # Define API URL
# url = f'https://nominatim.openstreetmap.org/search?format=json&q={location}'
#
# # Make request to API
# response = requests.get(url)
#
# # Parse JSON response
# data = response.json()
#
# if data:
#     return data[0]['lat'], data[0]['lon']
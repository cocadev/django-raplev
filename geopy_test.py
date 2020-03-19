from geopy import GoogleV3

GOOGLE_API_KEY = 'AIzaSyDjN61hLnxRZJtMWWf_E-r7MThLVRPtgj0'

postcodes = [{
    'country': 'Bulgaria',
    'city': 'Sofia',
    'postcode': '1000'
    }, {
    'country': 'Moldova',
    'city': 'Chisinau',
    'postcode': '2001'
    }, {
    'country': 'Ukraine',
    'city': 'Kiev',
    'postcode': '03134'
}, {
    'country': 'Denmark',
    'city': 'Copenhagen',
    'postcode': '1112'
}, {
    'country': 'Sweden',
    'city': 'Uppsala',
    'postcode': '752 29'
}, {
    'country': 'Estonia',
    'city': 'Talinn',
    'postcode': '10132'
}, {
    'country': 'China',
    'city': 'Shenzhen',
    'postcode': '518012'
}, {
    'country': 'China',
    'city': 'Fuzhou',
    'postcode': '350022'
}, {
    'country': 'Russia',
    'city': 'Moscow',
    'postcode': '105122'
}]

geo_locator = GoogleV3(api_key=GOOGLE_API_KEY)
for location in postcodes:
    geo_location = geo_locator.geocode(components={
        'country': location.get('country'),
        'locality': location.get('city'),
        'postal_code': location.get('postcode')
    })
    if geo_location:
        #print(geo_location.raw)
        print('https://www.google.com/maps/place/?q=place_id:{}'.format(geo_location.raw.get('place_id', )))
    else:
        print('Location {country}, {city}, {postcode} not found'.format(country=location.get('country'),
                                                                        city=location.get('city'),
                                                                        postcode=location.get('postcode')))

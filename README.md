
# Weather Forecast API

This document describes the endpoints and usage of the Weather Forecast API made by Giulia Simoncini for the exam: "Progettazione e produzione multimediale" (B003712).

## Structure

The API is organized around a single resource: `forecasts`. The endpoints are designed to allow users to retrieve, create, delete, and update weather forecasts.

Endpoint | HTTP Method | Description
-- | -- |--
`/api/weather_forecast/forecasts/` | GET | Get all forecasts (supports filtering by user)
`/api/weather_forecast/forecasts/create/` | POST | Create a new forecast
`/api/weather_forecast/forecasts/delete/<int:forecast_id>/` | DELETE | Delete a specific forecast
`/api/weather_forecast/forecasts/toggle-alert/<int:forecast_id>/` | PATCH | Toggle the weather alert status for a specific forecast
`/api/weather_forecast/forecasts/list/` | GET | Get all forecasts (class based view)

## Use

You can test the API using Httpie, a user-friendly HTTP client.

Install httpie using pip:

```bash
pip install httpie
```
First, ensure your Django development server is running:

```bash
python  manage.py  runserver
```
### Authentication
This API requires authentication for most of its endpoints. You need to obtain an authentication token. Once you have a token, include it in the Authorization header of your requests.
To get a  token the API offers the following endpoints:
- `/api/auth/register/ email="your_email" username="your_username"  password="your_password" password2="your_password"` to register your user account. 
- `/api/auth/token/ username="your_username" password="your_password"` to get your token:
	```JSON
	{
	"refresh": "token1",
	"access": "token2"
	}
	```
	We get two tokens, the access token will be used to authenticate all the requests we need to 		make, but this token will expire after a while. We can use the refresh token to request a new access token.
- `/api/auth/token/refresh/ refresh="your_token"` this will return a new access token.

Example of an unauthenticated request (will result in an error):
```bash
http  http://127.0.0.1:8000/api/weather_forecast/forecasts/
```
Example of an authenticated request using a token:
```bash
http  http://127.0.0.1:8000/api/weather_forecast/forecasts/  "Authorization: Bearer YOUR_AUTH_TOKEN"
```
Replace YOUR_AUTH_TOKEN with your actual authentication token.

### API Restrictions
There are three types of users:
- Anonymous user: it is an unauthenticated user which can access the api only for POST request, with a maximum of 10 requests per day.
- Authenticated user: it is an authenticated user which can access the api without restrictions; it can do all types of request. 
- Premium user: it is an authenticated user which has all the benefits of an authenticated user plus the possibility of saving and seeing his query history.

The API also has the following restrictions:
- Only the creator (authenticated) of a forecast may delete it.
- Only the creator (authenticated) of a forecast may toggle its weather alert status.

### Commands
Here are examples of how to call the API endpoints using httpie :

#### Get requests:
Get all forecasts:
- 	```bash
	http http://127.0.0.1:8000/api/weather_forecast/forecasts/ "Authorization: Bearer YOUR_AUTH_TOKEN"
	```

or, using the class based view:
-	```bash
	http http://127.0.0.1:8000/api/weather_forecast/forecasts/list/ "Authorization: Bearer YOUR_AUTH_TOKEN"
 	```

Get forecasts for a specific user:

```bash
http http://127.0.0.1:8000/api/weather_forecast/forecasts/?user=username "Authorization: Bearer YOUR_AUTH_TOKEN"
```
Replace username with the desired username.

---
#### Post requests:
Create a new forecast:
```bash
http POST http://127.0.0.1:8000/api/weather_forecast/forecasts/create/ "Authorization: Bearer YOUR_AUTH_TOKEN" region="Europe" country="France" condition="sunny" temperature=25.5 humidity=60 wind_speed=15 air_quality=15 weather_alert=false
 ```
Adjust the JSON data in the request body as needed.

---
#### Delete requests:
Delete a forecast:
```bash
http DELETE http://127.0.0.1:8000/api/weather_forecast/forecasts/delete/forecast_id/ "Authorization: Bearer YOUR_AUTH_TOKEN"
 ```
Replace forecast_id with the ID of the forecast to delete.

---
#### Patch requests:
Toggle weather alert for a forecast:
```bash
http PATCH http://127.0.0.1:8000/api/weather_forecast/forecasts/toggle-alert/forecast_id/ "Authorization: Bearer YOUR_AUTH_TOKEN" weather_alert=true
 ```
Replace forecast_id with the ID of the forecast and true with false to set the desired alert status.

---
#### Filtering
The /api/weather_forecast/forecasts/ endpoint supports filtering by the creator's username using the user query parameter:
```bash
http http://127.0.0.1:8000/api/weather_forecast/forecasts/?user=anotheruser "Authorization: Bearer YOUR_AUTH_TOKEN"
 ```
This will return only the forecasts created by the user anotheruser.

---
### Additional endpoints:
The API has a few additional endpoints to manage the user profile, those are meant to be used through the frontend but can still be accessed from the terminal.

#### See your profile:
```bash
http http://127.0.0.1:8000/api/auth/profile/ "Authorization: Bearer YOUR_AUTH_TOKEN"   
 ```
This will display your profile settings like this:
```JSON
{
    "daily_request_count": your_number_of_requests,
    "email": "your_email",
    "is_premium": your_status,
    "last_request_date": your_last_request_date,
    "username": "your_username"
}
```

---
#### Upgrade to premium:
```bash
http POST http://127.0.0.1:8000/api/auth/upgrade/ "Authorization: Bearer YOUR_AUTH_TOKEN"
```
This will upgrade your profile to premium.

---
#### See your query history:
```bash
http http://127.0.0.1:8000/api/auth/query-history/ "Authorization: Bearer YOUR_AUTH_TOKEN"
```
This will display your query history only if you are a premium user, an example output is the following:
```JSON
[
    {
        "country": "your_country",
        "date": "your_date_time",
        "id": forecast_id,
        "region": "your_region",
        "username": "your_username"
    },
	{
		...
	}
]
```
---
### Cleaning the database after use
If you are running the api locally and for any reason you want to delete the data in the database (located in a sqlite file in the project), run the following command:
```bash
python manage.py flush
```
Be careful it is a critical command as it will completely wipe your local database.

---
### Seeing the request limits from a local (terminal) server
As previously stated anonymous user can only make up to 10 POST requests per day. Unfortunately, if running with httpie it will not show any error messages even after exceeding your daily limit. To force the retention of the session use the following flag before your request: 
```bash
http --session=anon_session your_request
```
For example:
```bash
http --session=anon_session POST http://localhost:8000/api/weather_forecast/forecasts/create/ region="Tuscany" country="Italy" condition="sunny" temperature=25 humidity=40 wind_speed=5 air_quality="5"      
```
After the tenth request, the following error message will be shown:
```JSON
{
    "detail": "Authentication credentials were not provided."
}
```

## Client
All of the API functions can be accessed through a simple and minimal frontend, created using vanilla HTML, Django templates, CSS and Javascript. 
The client handles every type request in a more  user-friendly manner.

## SQL Tables
There are a few different tables used by differnt parts of the app.
### Forecast tables:
Used to model forecasts:

#### Location
Attribute | Type | Description
-- | -- | --
Id | Serial (autoincrement) | Primary key of the table
Region | CharField (string) | The region of the forecast
Country | CharField (string) | The country of the forecast
| | |
---
#### Condition
Attribute | Type | Description
-- | -- | --
Id | Serial (autoincrement) | Primary key of the table
Condition | CharField (string) | The condition of the forecast (chosen from a selection of 4)
Temperature | Decimal | The temperature of the forecast
Humidity | Decimal | The humidity of the forecast
Wind Speed | Decimal | The wind speed of the forecast
Air Quality | Decimal | The air quality of the forecast
| | |
---
#### Forecast
Attribute | Type | Description
-- | -- | --
Id | Serial (autoincrement) | Primary key of the table
Location | Number | Foreign key references Location.Id
Condition | Number | Foreign key references Condition.Id
Date | date_time | The date and time of the forecast
Weather alert | Boolean | The weather alert of the forecast
Creator | Number | Foreign key references CustomUser.ID
| | |
---
### Authentication tables:
#### CustomUser:
Only the additions from the standard django user are shown here:
Attribute | Type | Description
-- | -- | --
is_premium | Boolean | Wether the user is premium or not
daily_request_count | Integer | Number of daily requests made
last_request_date | Date | The date of the last request
| | |
---

#### QueryHistory:
Attribute | Type | Description
-- | -- | --
User | Number | Foreign key references CustomUser.ID
Region | CharField (string) | The region of the forecast
Country | CharField (string) | The country of the forecast
date | DateTime | The Date and the time of the request (or forecast)
| | |

# need to send join hung-cool to twilio whatsapp number to activate twilio sandbox.
# After it will be able to send whatsapp messages.
import requests, smtplib, os
from datetime import datetime
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
AV_API_KEY = os.environ['AV_API_KEY']
NEWS_API_KEY = os.environ['NEWS_API_KEY']
my_email = "marshhectar@gmail.com"
password = os.environ['password']
account_sid = os.environ['account_sid']
auth_token = os.environ['auth_token']

now = datetime.now()
year = now.year
month = now.month
day = now.day-1
date = f'{year}-{month}-{day}'

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
params = {
    'function': "TIME_SERIES_DAILY",
    'symbol': "TSLA",
    'apikey': AV_API_KEY,
}
AV_ENDPOINT = " https://www.alphavantage.co/query"

response = requests.get(AV_ENDPOINT, params=params)
data = response.json()
yesterday = float(list(data['Time Series (Daily)'].items())[0][1]['4. close'])
day_before_yesterday = float(list(data['Time Series (Daily)'].items())[1][1]['4. close'])
difference = yesterday - day_before_yesterday
pct_change = difference/day_before_yesterday * 100
if pct_change <= -5 or pct_change >= 5:
    ## STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
    news = []
    params = {
        'q': 'tesla',
        'from': f'{date}',
        'sortBy': 'publishedAt',
        'apiKey': NEWS_API_KEY,
    }
    NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    data = response.json()
    s = 0
    n = 0
    while s < 3:
        headline = data['articles'][n]['title']
        brief = data['articles'][n]['description']
        if headline == '[Removed]':
            print(f'skip {n+1}')
            n += 1
        else:
            news.append({'id': n+1, 'Headline': headline, 'Brief': brief})
            s += 1
            n += 1

    ## STEP 3: Use https://www.twilio.com
    # Send a seperate message with the percentage change and each article's title and description to your phone number.
    for n in range(3):
        message_increase = (f"Subject:Stock Price Alert\n\n"
                   f"{STOCK}: 🔺 {pct_change}%\n\n"
                   f"Headline: {news[n]['Headline']}\n\n"
                   f"Brief: {news[n]['Brief']}")
        message_decrease = (f"Subject:Stock Price Alert\n\n"
                   f"{STOCK}: 🔻 {pct_change}%\n\n"
                   f"Headline: {news[n]['Headline']}\n\n"
                   f"Brief: {news[n]['Brief']}")
        if pct_change < 0:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_="whatsapp:+14155238886",
                body=f"{message_decrease}",
                to="whatsapp:+917021615621",
            )
            print(message.status)
        else:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_="whatsapp:+14155238886",
                body=f"{message_increase}",
                to="whatsapp:+917021615621",
            )
            print(message.status)
else:
    print('skip')


#Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

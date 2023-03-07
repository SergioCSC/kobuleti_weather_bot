# Telegram weather bot

This is code of my Telegram bot for weather: https://t.me/kobuleti_weather_bot

It uses weather data from https://meteoblue.com and https://openweathermap.org

## Requirements

To run this code, you have to create **api_keys.py** file in project folder with such variables:

```python
OPENWEATHERMAP_ORG_APP_ID = 'your-openweathermap.org-app-id'
TELEGRAM_BOT_TOKEN = 'your-telegram-bot-token'
```
So you have to create account on https://openweathermap.org, and also create bot in Telegram.

### Run on AWS Lambda

My bot hosts on **Amazon Lambda**. If you want host it there too:

* Create AWS Lambda function
* Use *python 3.9* runtime for it
* Create API gateway trigger in your Lambda and use it as a webhook for telegram bot using such HTTP request:

      https://api.telegram.org/bot*your-bot-token-here*/setWebhook?url=*lambda-trigger-url-here*

* Add *pandas* layer (version 3) to your Lambda function 
* The sole python library which doesn't exists in this layer is *pillow* and it must be contained in *libs_for_aws_lambda* folder, so install *pillow* to this folder: 
    ```console
    pip install Pillow --target libs_for_aws_lambda --upgrade --python 3.9 --only-binary=:all:
    ```

### Run locally

If you want to run this code locally, you need to install python libraries *boto3, pillow and requests*:

```console
pip install -r requirements.txt
```

Then run

```console
python main.py
```
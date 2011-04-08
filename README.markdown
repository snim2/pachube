# Various hacks which all connect to pachube.com

## Pachube API keys

To use any of these scripts, you need to create a new file called **keys.py** which should contain this code:

    API_KEY = 'YOUR PERSONAL API KEY'
    API_URL = 'YOUR PERSONAL API URL, LIKE /api/1275.xml'

## Hacks

  * **laptop.py** reads sensor data from a laptop and publishes it as a pachube feed.
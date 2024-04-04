import sys,os
import requests
import urllib.parse
import lxml

import dataclasses
from typing import Optional,List,Union

from bs4 import BeautifulSoup

import selenium
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService

from webdriver_manager.firefox import GeckoDriverManager

# import geckodriver_autoinstaller


# geckodriver_autoinstaller.install()  # Check if the current version of geckodriver exists
#                                      # and if it doesn't exist, download it automatically,
#                                      # then add geckodriver to path
                
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
#driverAutoInstalled = webdriver.Firefox()


# import dotenv

# dotenv.load_dotenv(os.path.join(os.path.dirname(__file__),'.env'))

import unicodedata
from unidecode import unidecode

def clean_string(input_string):
    # Remove non-ASCII characters
    #ascii_string = ''.join(char for char in input_string if ord(char) < 128)
    ascii_string = unidecode(input_string)
    # Remove apostrophes
    cleaned_string = ascii_string.translate(str.maketrans('', '', "'"))
    
    return cleaned_string


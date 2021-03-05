import csv
import sqlite3
import requests
import re
import os
import shutil
import py7zr
import numpy as np


url = 'https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?dir=comext%2FCOMEXT_DATA%2FPRODUCTS'
file_base_url = 'https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=comext%2FCOMEXT_DATA%2FPRODUCTS%2F'


# some necessairy paths
#root_path = '/home/ec2-user/studies/estat-hckt-el-study/COMEXT/'
root_path = '/../datasets/COMEXT/'
download_path = os.path.join(root_path, 'downloaded')
extract_path = os.path.join(root_path, 'extracted')

# remove - WARNING
# shutil.rmtree(root_path)
# shutil.rmtree(download_path)
# shutil.rmtree(extract_path)

# create them if they don't exist
try:
    os.makedirs(download_path)
except Exception as e:
    print(e)

try:
    os.makedirs(extract_path)
except Exception as e:
    print(e)


cols = ['DECLARANT', 'DECLARANT_ISO', 'PARTNER', 'PARTNER_ISO', 'TRADE_TYPE', 'PRODUCT_NC', 'PRODUCT_SITC', 'PRODUCT_cpa2002', 'PRODUCT_cpa2008',
        'PRODUCT_CPA2_1', 'PRODUCT_BEC', 'PRODUCT_SECTION', 'FLOW', 'STAT_REGIME', 'SUPP_UNIT', 'PERIOD', 'VALUE_IN_EUROS', 'QUANTITY_IN_KG', 'SUP_QUANTITY']

# scrap url
r = requests.get(url)

# get all possible files
suffixes = np.array(re.findall('full[0-9]*.7z', r.text))
unique_suffixes = np.unique(suffixes)

con = sqlite3.connect('~/comext.db')

for i, suffix in enumerate(unique_suffixes):
    print(i, suffix)

    to_download_url = file_base_url + suffix

    to_save_path = os.path.join(download_path, suffix)
    r7z = requests.get(to_download_url, allow_redirects=True)
    open(to_save_path, 'wb').write(r7z.content)

    # to_extract_path = os.path.join(extract_path, suffix)

    archive = py7zr.SevenZipFile(to_save_path, mode='r')
    archive.extractall(path=extract_path)
    archive.close()

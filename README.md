# eu_bd_hackathon_gr
The entry for the Greek team participating in the Eurostat Big Data Hackathon of 2021

## Brief description
A web dashboard (built in Dash) that allows one to correlate intra-EU and extra-EU (as depicted
in the [COMEXT](https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?dir=comext%2FCOMEXT_DATA%2FPRODUCTS) 
dataset ) trade data with
Covid19-related metrics, in order to identify how the pandemic influenced the trade
volume for a country. The trading landscape is depicted as a graph in which countries
are nodes and edges are imports or exports. The dashboard also provides information about
the temporal evolution
of the trade volume for a selected product/country over the previous 12 months, alongside
the 12 month temporal evolution of Covid19 metrics for the same country. Finally, it computes correlations 
between imports/exports of the selected product vs Covid19 metrics such as new cases, deaths
and active cases.

![dashboard1](/sample.png)
![dashboard2](/sample2.png)

## How to run the dashboard
### Preparatory steps
* Download code and setup environment
```bash
git clone https://github.com/alpapado/eu_bd_hackathon_gr
cd eu_bd_hackathon_gr
conda env create -f environment.yml
```
* Download COMEXT data and build sqlite database
```bash
cd src
python get_comext_data.py
cd ../datasets/COMEXT/extracted
cat -n 1 full200001.dat > all.csv
tail -n +2 -q *.dat > all.csv
cd ../../
sqlite3 comext.db << EOF
.mode csv
.import COMEXT/extracted/all.csv
EOF
rm -r COMEXT
```

* Run dashboard
```
cd src
python dashboard_comext.py
```![dashboard1](https://user-images.githubusercontent.com/11426919/110153232-75148e00-7deb-11eb-8b49-ecd760c155af.png)

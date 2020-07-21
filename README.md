### Fly Home App
This app use skyscanner api to search flights instead of web crawler. So the speed is much faster and dates range can be larger.

##### Try Fly Home App

http://abcaab810fcb.ngrok.io

#### How to use?

##### System Requirements
```buildoutcfg
Operating System: MacOS/Linux
Python: version>=3.6
```
##### Step 1
Run the following command:
```buildoutcfg
python setup.py install
```
or 
```buildoutcfg
pip install -r requirements.txt
```

##### Step 2
Register an account to use [skyscanner](https://rapidapi.com/skyscanner/api/skyscanner-flight-search?endpoint=5aa1edd5e4b06ec3937b23f0)
After registration, get api key and export in your environment.
```buildoutcfg
export rapidapi_host=replace_with_your_rapidapi_host
export rapidapi_key=replace_with_your_rapidapi_key
```

##### Step 3
Start running Fly Home App
```buildoutcfg
streamlit run run.py
```

##### Step 4
After running the above command, your browser should open a page with the following address:
```buildoutcfg
localhost:8501
```
Bingo, you can play with it.


*Two resources are partially used in this project: [Vincent-Cui](https://github.com/Vincent-Cui/flights_checker) and [USCreditCardGuide](https://github.com/USCreditCardGuide/airlines-to-china-covid-19)*
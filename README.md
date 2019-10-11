# EthMusMIR - Anaylsis Server


Architecture is heavily inspired by (copied from) the Falcon API [First Steps Tutorial](https://falcon.readthedocs.io/en/stable/user/tutorial.html#first-steps)

Based on Python 3.5

## Install with Conda

### Ubuntu
```
cd ethmusmir
conda env create -f environment.yml
conda activate EthMusMIR
```
### OSX
```
conda env create --name EthMusMIR -f environment-osx.yml -v
```

## Run Server with

 ```
mkdir tmp
LOOK_STORAGE_PATH=tmp/ gunicorn --reload 'mirserver.app:get_app()'
```


## Sent Wave File for analysis

 from somewhere else ..

 ```
http POST localhost:8000/audio Content-Type:audio/wav < epianoC2.wav
```

You should receive:
 ```
HTTP/1.1 201 Created
Connection: close
Date: Tue, 08 Oct 2019 16:13:57 GMT
Server: gunicorn/19.9.0
content-length: 59
content-type: application/json; charset=UTF-8
location: /audio/2add4100-6630-4521-a4cc-128da173c257.wav

{
    "track": {
        "duration": 3.0229931972789115,
        "tempo": "nan"
    }
}
```

Added code from: M. Marolt, C. Bohak, A. Kavčič, and M. Pesek, "Automatic segmentation of ethnomusicological field recordings," Applied sciences, vol. 9, iss. 3, pp. 1-12, 2019.

 ```
HTTP/1.1 201 Created
Connection: close
Date: Thu, 10 Oct 2019 14:47:41 GMT
Server: gunicorn/19.9.0
content-length: 387
content-type: application/json; charset=UTF-8
location: /audio/b35fb930-90d1-42a6-a870-24d3e9713a09.wav

{
    "track": {
        "duration": 11.0120625,
        "parts": [
            {
                "content": "speech",
                "duration": 1,
                "start": 0
            },
            {
                "content": "solo singing",
                "duration": 2,
                "start": 1
            },
            {
                "content": "instrumental",
                "duration": 1,
                "start": 3
            },
            {
                "content": "choir singing",
                "duration": 3,
                "start": 4
            },
            {
                "content": "solo singing",
                "duration": 1,
                "start": 7
            },
            {
                "content": "speech",
                "duration": 2,
                "start": 8
            }
        ],
        "tempo": "nan"
    }
}
```

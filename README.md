# EthMusMIR - Anaylsis Server


Architecture is heavily inspired (copied) by the Falcon API [First Steps Tutorial](https://falcon.readthedocs.io/en/stable/user/tutorial.html#first-steps)

Based on Python 3.5

## Install with Conda
```
conda env create -f environment.yml
conda activate EthMusMIR
```

## Run Server with

 ```
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

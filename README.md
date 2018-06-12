> *Aetrapp Image Processing Service*

*Work in progress*

## Developing

First, start the server:

    docker-compose up

Then, access the dashboard at http://localhost:3131/agenda. To create your first job, make a POST request to `/agenda/api/jobs/create` like in the following example. You can change "imageUrl" value to any image available:

````shell
curl -H "Content-Type: application/json" -X POST -d \
    '{
      "jobName": "process image",
      "jobSchedule": "now",
      "jobData": {
         "image": {
             "url": "https://github.com/aetrapp/image-processing-service/raw/master/samples/06.4SEM.CENC.INTRA.SONY.jpg"
         }
      }
     }' http://localhost:3131/agenda/api/jobs/create
````

If you need shell access to the server, get your container name with `docker ps` and run:

    docker exec -i -t <imageprocessingservice_container_name> /bin/bash

### Deploying new version to production

AeTrapp's main API server checks every five minutes the current version of the Image Processing Server, and will perform re-analysis of samples if a new version is found. To start this process:

- Change algorithms code and commit;
- Change `ipsVersion` value in `package.json` and commit:

```json
{
  "name": "image-processing-service",
  "version": "0.0.1",
  "ipsVersion": "1.4.0",
  "description": "Aetrapp Image Processing Service",
...
```

- Pull changes to production.

This will start automatically the processes of sample re-analysis by the API server.

# Changelog

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 1.4.1

Released: June 12, 2018

To be described.

## License

[GPL-3.0](LICENSE)

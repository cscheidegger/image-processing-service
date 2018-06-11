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

### Upgrading python scripts

For modifications in python scripting to take effect, it is needed to update the property `ipsVersion` in `package.json` file. The AeTrapp's API server will reach endpoint `/api/description` of this IPS to check if there is a new algorithm version available. If so, it will start an re-analysis of samples every X minutes.

## Changelog

No releases yet.

## License

[GPL-3.0](LICENSE)

> *Aetrapp Image Processing Service*

*Work in progress*

## Developing

First, start the server:

  docker-compose up

Then, access the dashboard at http://localhost:3030/agenda. To create your first job, make a POST request to `/scheduler/api/jobs/create` like the following example. You can change "imageUrl" value to any online image:

````shell
curl -H "Content-Type: application/json" -X POST -d \
    '{
      "jobName": "process image",
      "jobSchedule": "now",
      "jobData": {
         "imageUrl": "https://github.com/aetrapp/image-processing-service/raw/master/samples/06.4SEM.CENC.INTRA.SONY.jpg"
      }
     }' http://localhost:3030/scheduler/api/jobs/create
````

If you need shell access to the server, get your container name with `docker ps` and run:

    docker exec -i -t <imageprocessingservice_container_name> /bin/bash

## Changelog

No releases yet

## LICENSE

GPL+3.0

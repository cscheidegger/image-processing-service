> *Aetrapp Image Processing Service*


Start shell in a Anaconda instance using Docker:
    
    docker run -i -v <repository_absolute_path>:/src -t continuumio/anaconda3 /bin/bash


`<repository_absolute_path>` is the repository absolute path on your machine. Then install remaining dependencies:

    conda install opencv3 keras tensorflow
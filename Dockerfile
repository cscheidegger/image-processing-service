FROM continuumio/anaconda3

WORKDIR /src

# Install Anaconda dependencies
RUN conda install -y opencv keras tensorflow \
  && conda clean -a -y

# Install APT dependencies 
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    libgtk2.0-dev \
  && rm -rf /tmp/* /var/lib/apt/lists/*  
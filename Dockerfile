FROM continuumio/anaconda3

WORKDIR /src

# Install Anaconda dependencies
RUN conda install -y opencv keras tensorflow \
  && conda clean -a -y
  
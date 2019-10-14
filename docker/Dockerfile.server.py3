# docker build -t johnbensnyder/byteps_server_py3:0.0.0-a -f Dockerfile.server.py3 .

FROM ubuntu:18.04

ENV LD_LIBRARY_PATH /root/incubator-mxnet/lib/:/usr/local/lib:$LD_LIBRARY_PATH

# To enable RDMA, add `USE_RDMA=1` to `SERVER_BUILD_OPTS` below.
ENV SERVER_BUILD_OPTS "USE_BLAS=openblas USE_MKL=1 USE_DIST_KVSTORE=1"
ENV BYTEPS_SERVER_MXNET_PATH /root/incubator-mxnet
ENV MXNET_SERVER_LINK https://github.com/bytedance/incubator-mxnet

ENV BYTEPS_BASE_PATH /usr/local
ENV BYTEPS_PATH $BYTEPS_BASE_PATH/byteps
ENV BYTEPS_GIT_LINK https://github.com/bytedance/byteps
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get install -y --allow-downgrades --allow-change-held-packages --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        curl \
        wget \
        vim \
        libopenblas-dev \
        liblapack-dev \
        libopencv-dev \
        python3 \
        python3-dev \
        python3-setuptools \
        libjemalloc-dev \
        graphviz \
        cmake \
        libjpeg-dev \
        libpng-dev \
        iftop \
        lsb-release

RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get update &&\
    apt-get -y install python3-pip &&\
    pip3 install --upgrade pip

RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN rm -f /usr/bin/pip && ln -s /usr/bin/pip3 /usr/bin/pip

RUN pip --no-cache-dir install \
        matplotlib \
        numpy==1.15.2 \
        scipy \
        sklearn \
        pandas \
        graphviz==0.9.0 \
        mxboard \
        tensorboard==1.0.0a6

WORKDIR /root/

RUN git clone --single-branch --branch byteps --recurse-submodules $MXNET_SERVER_LINK

RUN cd $BYTEPS_SERVER_MXNET_PATH && \
    make clean_all && make -j16 $SERVER_BUILD_OPTS

RUN cd $BYTEPS_SERVER_MXNET_PATH && \
    cd python && \
    python setup.py build && \
    python setup.py install &&\
    python setup.py bdist_wheel

RUN cd $BYTEPS_BASE_PATH &&\
    git clone --recurse-submodules $BYTEPS_GIT_LINK

RUN apt-get install -y git && \
	git clone openmpi

FROM inklesspen/s6-py3-node:latest

# mcron install
RUN gpg --keyserver pool.sks-keyservers.net --recv-keys 856EA44B2DDC5C8BDF659F44E4A28AAC31182342

ENV MCRON_VERSION 1.0.8
RUN set -x \
    && apt-get update && apt-get install -y --no-install-recommends guile-2.0 guile-2.0-dev ed \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && curl -SL "ftp://ftp.gnu.org/pub/gnu/mcron/mcron-$MCRON_VERSION.tar.gz" -o mcron.tar.gz \
    && curl -SL "ftp://ftp.gnu.org/pub/gnu/mcron/mcron-$MCRON_VERSION.tar.gz.sig" -o mcron.tar.gz.sig \
    && gpg --verify mcron.tar.gz.sig \
    && mkdir -p /usr/src/mcron \
    && tar -xzC /usr/src/mcron --strip-components=1 -f mcron.tar.gz \
    && rm mcron.tar.gz* \
    && cd /usr/src/mcron \
    && ./configure \
    && make \
    && make install \
    && rm -rf /usr/src/mcron
# end mcron install

EXPOSE 8080

WORKDIR /

COPY package.json /
RUN npm install

COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install --upgrade setuptools && pip install --upgrade wheel && pip install -r /tmp/requirements.txt

ADD . /code
WORKDIR /code

RUN pip install .

# move this up above npm install, later, once the etc stuff is stable
ADD etc /etc/

ENTRYPOINT ["/init"]

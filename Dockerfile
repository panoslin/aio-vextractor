FROM python:3.7
ENV PYTHONUNBUFFERED 1
ADD requirements.txt /aioVextractor/
##  添加国内镜像源
RUN mkdir -p /root/.pip/ \
ADD pip.conf /root/.pip/pip.conf
WORKDIR /aioVextractor
RUN apt-get update \
    && apt-get install -y ffmpeg \
    && pip3 install --upgrade pip \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN pip3 install -r requirements.txt \
    && pyppeteer-install

RUN apt-get install -yq --no-install-recommends \
    libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 \
    libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
    libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    libnss3
#ENV PATH=/usr/local/bin:/usr/local/sbin:/sbin:/bin:/usr/sbin:/usr/bin:/root/bin
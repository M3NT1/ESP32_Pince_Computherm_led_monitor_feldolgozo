ARG BUILD_FROM
FROM $BUILD_FROM

# Környezeti változók
ENV LANG C.UTF-8
ENV PYTHONUNBUFFERED=1

# Python és függőségek telepítése
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-numpy \
    opencv \
    py3-opencv \
    && pip3 install --no-cache-dir --break-system-packages \
        Flask==3.0.0 \
        requests==2.31.0 \
        paho-mqtt==1.6.1

# Munkakönyvtár létrehozása
WORKDIR /app

# Alkalmazás fájlok másolása
COPY app.py /app/
COPY templates/ /app/templates/
COPY run.sh /app/

# Script futtathatóvá tétele
RUN chmod a+x /app/run.sh

# Alkalmazás indítása
CMD [ "/app/run.sh" ]

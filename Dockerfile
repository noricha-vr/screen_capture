FROM python:3.10-buster
# fonts-takao-*                             # jp (Japanese) fonts
# ttf-wqy-microhei fonts-wqy-microhei       # kr (Korean) fonts
# fonts-arphic-ukai fonts-arphic-uming      # cn (Chinese) fonts

# Install manually all the missing libraries
RUN apt-get update && apt-get install -y  \
    ffmpeg\
    gconf-service  \
    libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0  \
    libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils wget \
    fonts-takao-* ttf-wqy-microhei fonts-wqy-microhei \
    fonts-arphic-ukai fonts-arphic-uming

# Install Brave
RUN apt-get update && apt-get install -y curl && \
    curl -s https://brave-browser-apt-release.s3.brave.com/brave-core.asc | apt-key --keyring /etc/apt/trusted.gpg.d/brave-browser-release.gpg add - && \
    sh -c 'echo "deb [arch=amd64] https://brave-browser-apt-release.s3.brave.com `lsb_release -sc` main" >> /etc/apt/sources.list.d/brave.list' && \
    apt-get update && apt-get install -y brave-browser

# Install Chrome Driver
RUN CHROME_DRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE) \
    && curl https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -o /tmp/chromedriver.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip


# Install Python dependencies.
COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . .

EXPOSE 8080

CMD exec uvicorn main:app --host 0.0.0.0 --port 8080

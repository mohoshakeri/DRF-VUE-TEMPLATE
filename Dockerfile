#FROM python:3.12-slim
FROM mirror-docker.runflare.com/library/python:3.12-slim

# APT Mirror and disable SSL
RUN sed -i 's/deb.debian.org/mirror-linux.runflare.com/g' /etc/apt/sources.list.d/debian.sources
RUN sed -i 's/security.debian.org/mirror-linux.runflare.com/g' /etc/apt/sources.list.d/debian.sources
RUN sed -i 's/https/http/g' /etc/apt/sources.list.d/debian.sources

ENV PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://mirror-pypi.runflare.com/simple

# Install Linux Dependencies
RUN apt-get update -o Acquire::Check-Valid-Until=false
RUN apt-get install -y --no-install-recommends build-essential libpq-dev libmagic1 bash curl gnupg nano supervisor nginx tzdata nodejs npm -o Acquire::Check-Valid-Until=false
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

# Install Supercronic
ENV SUPERCRONIC_URL=https://iamshakeri.ir/fs/supercronic-linux-amd64-0.2.39 \
    SUPERCRONIC_SHA1SUM=c98bbf82c5f648aaac8708c182cc83046fe48423 \
    SUPERCRONIC=supercronic-linux-amd64-0.2.39
RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

# Set TZ
ENV TZ=Asia/Tehran
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN echo $TZ > /etc/timezone

# Create app directory
WORKDIR /app

# Copy source
COPY . ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Vue dependencies
WORKDIR /app/client
RUN npm config set registry https://mirror-npm.runflare.com
RUN npm install
RUN npx vite build

# Create necessary directories
RUN mkdir -p /var/log/xxx

# System Config Files
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx.conf /etc/nginx/nginx.conf

# File Access
RUN chmod 644 /app/templates/robots.txt
RUN chmod 644 /app/templates/sitemap.xml


# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

# Only expose Nginx port (gateway)
EXPOSE 80
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf", "-n"]

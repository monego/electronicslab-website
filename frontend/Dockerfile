FROM node:lts-trixie-slim

RUN npm install -g @quasar/cli

ARG API_URL
ENV API_URL=$API_URL

WORKDIR /app

COPY . .
RUN npm install --legacy-peer-deps

EXPOSE 8080

CMD ["quasar", "dev", "-m", "spa", "--hostname", "0.0.0.0"]

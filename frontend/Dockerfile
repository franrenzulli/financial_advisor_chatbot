# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json ./
COPY package-lock.json ./
RUN npm install

COPY . .

# RUN npm run build

CMD ["npm", "start"]
FROM node:22-alpine AS build
WORKDIR /app
COPY frontend/package*.json /app/frontend/
WORKDIR /app/frontend
RUN npm ci
COPY frontend /app/frontend
COPY datasets/samples /app/datasets/samples
RUN npm run build
FROM nginx:alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/frontend/dist /usr/share/nginx/html
EXPOSE 80

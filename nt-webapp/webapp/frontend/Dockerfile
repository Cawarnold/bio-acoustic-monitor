# Stage 1: Build
FROM node:22-alpine AS build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve
FROM nginx:stable-alpine
# Copy the built 'dist' folder to Nginx's serve directory
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Copy the config from your frontend folder to Nginx's config directory
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
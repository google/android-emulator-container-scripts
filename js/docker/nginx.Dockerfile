# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
# Build stage
FROM node:20-alpine as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

# Production stage
FROM nginx:1.21-alpine as production-stage

COPY --from=build-stage /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
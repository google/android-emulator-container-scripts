# Stage 0, "build-stage", based on Node.js, to build and compile the frontend
# FROM tiangolo/node-frontend:10 as build-stage
FROM node:14.5 as build-stage
WORKDIR /app
COPY ./ /app/
RUN yarn
ARG configuration=production
RUN npm run build
# Stage 1, based on Nginx, to have only the compiled app, ready for production with Nginx
FROM nginx:1.19
COPY --from=build-stage /app/build/ /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

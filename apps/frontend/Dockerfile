FROM node:20-alpine AS build
WORKDIR /app
COPY apps/frontend/package.json /app/package.json
COPY apps/frontend/vite.config.ts /app/vite.config.ts
COPY apps/frontend/tsconfig.json /app/tsconfig.json
COPY apps/frontend/index.html /app/index.html
COPY apps/frontend/src /app/src
RUN npm install
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

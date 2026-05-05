# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first (layer caching)
COPY package*.json ./

# Explicitly install ALL deps including devDependencies
# Do NOT set NODE_ENV=production before this step
RUN npm ci

# Copy source code
COPY . .

# Set NODE_ENV only for the build step, not for npm install
RUN NODE_ENV=production npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
# Stage 1: Build
FROM node:20-alpine AS build

WORKDIR /app

# Make sure devDependencies like vite are installed
ENV NODE_ENV=development

# Copy package files
COPY package*.json ./

# If package-lock.json exists, this is better than npm install
RUN npm ci --include=dev

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
# Multi-stage build for React frontend
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package.json ./

# Install dependencies (using --legacy-peer-deps to resolve React 18 conflicts)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built app
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]

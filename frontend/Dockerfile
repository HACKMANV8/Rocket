# ===========================
# Stage 1: Build Angular app
# ===========================
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies including devDependencies (for build tools like webpack)
RUN npm install --legacy-peer-deps --no-audit --no-fund --include=dev

# Copy application source code
COPY . .

# Ensure Angular CLI is installed globally
RUN npm install -g @angular/cli

# Build Angular app for production
RUN npx ng build --configuration=production

# ===========================
# Stage 2: Serve with Nginx
# ===========================
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Remove default nginx static files
RUN rm -rf /usr/share/nginx/html/*

# Copy custom nginx config (if available)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built Angular app from build stage
# ⚠️ Make sure the path below matches your Angular "outputPath" in angular.json
# Example: "outputPath": "dist/mining-frontend/browser"
COPY --from=build /app/dist/mining-copilot/browser /usr/share/nginx/html

# Set proper file permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Expose container port
EXPOSE 80

# Add a simple health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:80/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

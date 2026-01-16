# Use Node.js LTS as base image
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy frontend code
COPY frontend/ ./frontend/

# Build the React app
RUN npm run build --prefix frontend

# Expose port 3000
EXPOSE 3000

# Command to run the app
CMD ["npm", "start", "--prefix", "frontend"]

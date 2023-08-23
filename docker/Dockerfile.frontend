# Use an official Node.js runtime as the base image
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json to the container
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm install --legacy-peer-deps

# Copy the rest of the application code to the container
COPY frontend/ ./

# Build the frontend app
# RUN npm run build

# Expose port 3000 for the frontend
EXPOSE 3000

# Start the React app
CMD ["npm", "start"]
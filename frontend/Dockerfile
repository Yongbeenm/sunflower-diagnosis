FROM node:22-slim

WORKDIR /app

# Copy dependency manifests first for efficient Docker layer caching
COPY package*.json ./
RUN npm install

# Copy source files
COPY . .

EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

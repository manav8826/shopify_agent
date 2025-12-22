FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

# Serve with a simple static server or just expose dev port (for this demo, we'll assume dev/build)
# For production, we'd use Nginx. For dev/demo:
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]

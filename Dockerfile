# Web EasyForLife na Fly (app easyforlife-redirect). Před nasazením: python3 build.py (vytvoří dist/).
FROM node:22-alpine
WORKDIR /app
COPY server/server.js ./
COPY dist ./dist
ENV PORT=8080
EXPOSE 8080
CMD ["node", "server.js"]

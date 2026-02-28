FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY frontend/package.json frontend/package-lock.json ./

# 安装依赖
RUN npm ci --silent

# 复制源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# Production stage
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
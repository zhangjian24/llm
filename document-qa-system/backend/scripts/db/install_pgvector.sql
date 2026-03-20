-- PostgreSQL pgvector 扩展安装脚本
-- 适用于 PostgreSQL 12+ 版本

-- 1. 安装 pgvector 扩展（需要管理员权限）
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. 验证扩展是否安装成功
SELECT extname, extversion 
FROM pg_extension 
WHERE extname = 'vector';

-- 3. 查看可用的向量操作符
SELECT oprname, oprleft::regtype, oprright::regtype, oprresult::regtype
FROM pg_operator 
WHERE oprname IN ('<->', '<#>', '<=>')
ORDER BY oprname;

-- 4. 创建测试表验证功能
CREATE TABLE IF NOT EXISTS vector_test (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1024)
);

-- 5. 创建向量索引（HNSW 算法，适用于余弦相似度）
CREATE INDEX IF NOT EXISTS idx_vector_test_embedding 
ON vector_test 
USING hnsw (embedding vector_cosine_ops);

-- 6. 插入测试数据
INSERT INTO vector_test (content, embedding) 
VALUES 
    ('测试文档1', ARRAY[random(), random(), random()]::VECTOR(1024)),
    ('测试文档2', ARRAY[random(), random(), random()]::VECTOR(1024));

-- 7. 验证查询功能
SELECT id, content, embedding <-> '[0.5, 0.5, 0.5]'::VECTOR(1024) as distance
FROM vector_test 
ORDER BY embedding <-> '[0.5, 0.5, 0.5]'::VECTOR(1024)
LIMIT 5;

-- 8. 清理测试数据
DROP TABLE IF EXISTS vector_test;

-- 安装完成！
-- 注意：HNSW 索引需要 PostgreSQL 14+ 和适当的编译选项
-- 如果 HNSW 不可用，可以使用 IVFFlat 索引作为替代：

/*
-- 替代索引方案（IVFFlat）
CREATE INDEX IF NOT EXISTS idx_vector_test_embedding_ivfflat 
ON vector_test 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
*/
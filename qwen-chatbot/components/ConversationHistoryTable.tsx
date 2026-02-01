import React from 'react';
import styles from '../styles/ConversationHistoryTable.module.css';

interface ConversationHistory {
  id: number;
  timestamp: string;
  input: string;
  output: string;
  model: string;
  params: {
    temperature: number;
    top_p: number;
    max_tokens: number;
  };
  tokenUsage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  evaluation: string;
}

interface ConversationHistoryTableProps {
  history: ConversationHistory[];
  onEvaluationChange: (id: number, evaluation: string) => void;
}

const ConversationHistoryTable: React.FC<ConversationHistoryTableProps> = ({ history, onEvaluationChange }) => {
  const formatDate = (timestamp: string) => {
    return new Intl.DateTimeFormat('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(timestamp));
  };

  const autoEvaluate = (output: string): string => {
    if (output.includes('Error:') || output.includes('error') || output.includes('失败')) {
      return '响应错误';
    }
    
    const wordCount = output.trim().split(/\s+/).length;
    
    if (wordCount < 5) return '响应过短';
    if (wordCount > 100) return '响应详细';
    return '响应适中';
  };

  return (
    <div className={styles.historyContainer}>
      <h3>对话历史记录</h3>
      {history.length === 0 ? (
        <p className={styles.noHistory}>暂无对话历史</p>
      ) : (
        <div className={styles.tableWrapper}>
          <table className={styles.historyTable}>
            <thead>
              <tr>
                <th>时间</th>
                <th>输入</th>
                <th>输出</th>
                <th>模型</th>
                <th>参数</th>
                <th>Token明细</th>
                <th>效果评估</th>
              </tr>
            </thead>
            <tbody>
              {history.map((item) => (
                <tr key={`history-${item.id}`}>
                  <td className={styles.timestamp}>{formatDate(item.timestamp)}</td>
                  <td className={styles.input}>{item.input}</td>
                  <td className={styles.output}>{item.output.substring(0, 180)}{item.output.length > 180 ? '...' : ''}</td>
                  <td className={styles.model}>{item.model}</td>
                  <td className={styles.params}>
                    <div><span className={styles.paramLabel}>温度:</span> {item.params.temperature.toFixed(2)}</div>
                    <div><span className={styles.paramLabel}>Top-P:</span> {item.params.top_p.toFixed(2)}</div>
                    <div><span className={styles.paramLabel}>最大Tokens:</span> {item.params.max_tokens}</div>
                  </td>
                  <td className={styles.tokenUsage}>
                    {item.tokenUsage ? (
                      <div>
                        <div><span className={styles.tokenLabel}>输入:</span> {item.tokenUsage.prompt_tokens}</div>
                        <div><span className={styles.tokenLabel}>输出:</span> {item.tokenUsage.completion_tokens}</div>
                        <div><span className={styles.tokenLabel}>总计:</span> {item.tokenUsage.total_tokens}</div>
                      </div>
                    ) : (
                      <div><span className={styles.noData}>未记录</span></div>
                    )}
                  </td>
                  <td className={styles.evaluation}>
                    <input
                      type="text"
                      value={item.evaluation}
                      onChange={(e) => onEvaluationChange(item.id, e.target.value)}
                      placeholder={item.evaluation || autoEvaluate(item.output)}
                      className={styles.evaluationInput}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ConversationHistoryTable;
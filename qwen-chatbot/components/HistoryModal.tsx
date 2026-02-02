import React from 'react';
import { ConversationHistory } from '../types';
import styles from '../styles/HistoryModal.module.css';

interface HistoryModalProps {
  history: ConversationHistory[];
  isOpen: boolean;
  onClose: () => void;
  onEvaluationChange: (id: number, evaluation: string) => void;
}

const HistoryModal: React.FC<HistoryModalProps> = ({ 
  history, 
  isOpen, 
  onClose,
  onEvaluationChange
}) => {
  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2>对话历史记录</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>
        
        <div className={styles.modalBody}>
          {history.length === 0 ? (
            <p className={styles.emptyState}>暂无对话历史记录</p>
          ) : (
            <div className={styles.historyTableContainer}>
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
                    <tr key={item.id}>
                      <td className={styles.timestampCell}>
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                      <td className={styles.inputCell}>
                        <div className={styles.cellContent}>
                          {item.input.substring(0, 50)}{item.input.length > 50 ? '...' : ''}
                        </div>
                      </td>
                      <td className={styles.outputCell}>
                        <div className={styles.cellContent}>
                          {item.output.substring(0, 80)}{item.output.length > 80 ? '...' : ''}
                        </div>
                      </td>
                      <td className={styles.modelCell}>{item.model}</td>
                      <td className={styles.paramsCell}>
                        <div className={styles.paramsDetail}>
                          <div>temperature: {item.params.temperature}</div>
                          <div>top_p: {item.params.top_p}</div>
                          <div>max_tokens: {item.params.max_tokens}</div>
                        </div>
                      </td>
                      <td className={styles.tokenCell}>
                        {item.tokenUsage && (
                          <div className={styles.tokenDetail}>
                            <div>Prompt: {item.tokenUsage.prompt_tokens}</div>
                            <div>Completion: {item.tokenUsage.completion_tokens}</div>
                            <div>Total: {item.tokenUsage.total_tokens}</div>
                          </div>
                        )}
                      </td>
                      <td className={styles.evaluationCell}>
                        <input
                          type="text"
                          value={item.evaluation}
                          onChange={(e) => onEvaluationChange(item.id, e.target.value)}
                          placeholder="请输入评价"
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
      </div>
    </div>
  );
};

export default HistoryModal;
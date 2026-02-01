import React from 'react';
import styles from '../styles/ModelConfigPanel.module.css';

interface ModelConfig {
  model: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
}

interface ModelConfigPanelProps {
  config: ModelConfig;
  onUpdateConfig: (config: ModelConfig) => void;
}

const ModelConfigPanel: React.FC<ModelConfigPanelProps> = ({ config, onUpdateConfig }) => {
  const handleChange = (field: keyof ModelConfig, value: any) => {
    onUpdateConfig({
      ...config,
      [field]: value
    });
  };

  // 预设模型列表 - 根据通义千问官方文档调整
  const modelOptions = [
    { value: 'qwen-turbo', label: 'Qwen-Turbo (Fast & Cheap)' },
    { value: 'qwen-plus', label: 'Qwen-Plus (Balance)' },
    { value: 'qwen-max', label: 'Qwen-Max (Most Capable)' },
    // 注意：qwen-max-0102 可能需要特殊权限，如遇404错误请使用 qwen-max
  ];

  return (
    <div className={styles.configPanel}>
      <h3>LLM Parameters</h3>
      <div className={styles.configRow}>
        <label htmlFor="model">Model:</label>
        <select
          id="model"
          value={config.model}
          onChange={(e) => handleChange('model', e.target.value)}
          className={styles.selectInput}
        >
          {modelOptions.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
      </div>
      
      <div className={styles.configRow}>
        <label htmlFor="temperature">Temperature: {config.temperature.toFixed(2)}</label>
        <input
          type="range"
          id="temperature"
          min="0"
          max="2"
          step="0.01"
          value={config.temperature}
          onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          className={styles.sliderInput}
        />
        <span className={styles.valueDisplay}>{config.temperature.toFixed(2)}</span>
      </div>
      
      <div className={styles.configRow}>
        <label htmlFor="top_p">Top-P: {config.top_p.toFixed(2)}</label>
        <input
          type="range"
          id="top_p"
          min="0"
          max="1"
          step="0.01"
          value={config.top_p}
          onChange={(e) => handleChange('top_p', parseFloat(e.target.value))}
          className={styles.sliderInput}
        />
        <span className={styles.valueDisplay}>{config.top_p.toFixed(2)}</span>
      </div>
      
      <div className={styles.configRow}>
        <label htmlFor="max_tokens">Max Tokens: {config.max_tokens}</label>
        <input
          type="range"
          id="max_tokens"
          min="1"
          max="8192"
          step="1"
          value={config.max_tokens}
          onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
          className={styles.sliderInput}
        />
        <span className={styles.valueDisplay}>{config.max_tokens}</span>
      </div>
    </div>
  );
};

export default ModelConfigPanel;
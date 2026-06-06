import React from 'react';
import type { ModelConfig } from '../types';
import { MODEL_OPTIONS } from '../lib/model-options';

interface ModelConfigPanelProps {
  config: ModelConfig;
  onUpdateConfig: (config: ModelConfig) => void;
  disabled?: boolean; // 当前处于角色模式时，某些配置可能被禁用
}

const ModelConfigPanel: React.FC<ModelConfigPanelProps> = ({
  config,
  onUpdateConfig,
  disabled = false,
}) => {
  const handleChange = (field: keyof ModelConfig, value: any) => {
    if (disabled) return;

    onUpdateConfig({
      ...config,
      [field]: value,
    });
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
      <h3 className="text-lg font-semibold text-gray-800 border-b border-gray-200 pb-3">
        LLM Parameters
      </h3>

      <div className="space-y-2">
        <label htmlFor="model" className="block text-sm font-medium text-gray-700">
          Model:
        </label>
        <select
          id="model"
          value={config.model}
          onChange={(e) => handleChange('model', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
          disabled={disabled}
        >
          {MODEL_OPTIONS.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label htmlFor="temperature" className="text-sm font-medium text-gray-700">
            Temperature: {config.temperature.toFixed(2)}
          </label>
          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {config.temperature.toFixed(2)}
          </span>
        </div>
        <input
          type="range"
          id="temperature"
          min="0"
          max="2"
          step="0.01"
          value={config.temperature}
          onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={disabled}
        />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label htmlFor="top_p" className="text-sm font-medium text-gray-700">
            Top-P: {config.top_p.toFixed(2)}
          </label>
          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {config.top_p.toFixed(2)}
          </span>
        </div>
        <input
          type="range"
          id="top_p"
          min="0"
          max="1"
          step="0.01"
          value={config.top_p}
          onChange={(e) => handleChange('top_p', parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={disabled}
        />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <label htmlFor="max_tokens" className="text-sm font-medium text-gray-700">
            Max Tokens: {config.max_tokens}
          </label>
          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {config.max_tokens}
          </span>
        </div>
        <input
          type="range"
          id="max_tokens"
          min="1"
          max="8192"
          step="1"
          value={config.max_tokens}
          onChange={(e) => handleChange('max_tokens', parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={disabled}
        />
      </div>
    </div>
  );
};

export default ModelConfigPanel;

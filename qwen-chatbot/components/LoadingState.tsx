/**
 * LoadingState - 统一的加载状态组件
 *
 * 替换所有内联"加载中" div，统一视觉与可访问性
 * - role="status" + aria-live="polite" 让屏幕阅读器自动播报
 */
export function LoadingState({ message = '加载中...' }: { message?: string }) {
  return (
    <div className="flex items-center justify-center p-8" role="status" aria-live="polite">
      <div
        className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"
        aria-hidden="true"
      />
      <span className="ml-3 text-gray-600">{message}</span>
    </div>
  );
}

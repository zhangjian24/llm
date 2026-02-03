// Tailwind CSS 使用指南

// 基础类名示例：
// 布局类
// - flex, grid, block, inline-block
// - justify-center, items-center
// - gap-4, space-x-2, space-y-3

// 尺寸类
// - w-full, h-screen, max-w-md
// - p-4, m-2, px-3, py-1
// - text-sm, text-lg, text-2xl

// 颜色类
// - bg-blue-500, text-red-600
// - border-gray-300
// - hover:bg-blue-600

// 响应式前缀
// - sm:w-full, md:flex, lg:hidden

// 实用示例：
/*
<div className="flex items-center justify-between p-4 bg-white shadow-md">
  <h1 className="text-xl font-bold text-gray-800">标题</h1>
  <button className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
    按钮
  </button>
</div>
*/

// 组件示例：
/*
const Card = ({ title, children }) => (
  <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
    <h3 className="text-lg font-semibold mb-4 text-gray-800">{title}</h3>
    <div className="text-gray-600">{children}</div>
  </div>
);
*/
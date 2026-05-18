/** [2026-05-18] 统一 API 根路径；Nginx 同域或 Vite 代理时 VITE_API_BASE 留空。 */

/**
 * 函数功能：读取环境变量中的 API 根 URL（无末尾斜杠）。
 * 输入说明：无（使用 `import.meta.env.VITE_API_BASE`）。
 * 输出说明：空字符串表示使用相对路径 `/api/...`。
 */
export function apiBase(): string {
  const b = import.meta.env.VITE_API_BASE ?? '';
  return b.replace(/\/$/, '');
}

/**
 * 函数功能：拼接完整 API URL。
 * 输入说明：`path` 以 `/` 开头的路径，如 `/api/analyze`。
 * 输出说明：``${apiBase()}${path}``。
 */
export function apiUrl(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${apiBase()}${p}`;
}

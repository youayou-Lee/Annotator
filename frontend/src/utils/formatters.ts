/**
 * 格式化文件大小为可读形式
 * 
 * @param bytes 文件大小（字节）
 * @param decimals 小数位数，默认为2
 * @returns 格式化后的文件大小字符串
 */
export const formatBytes = (bytes: number, decimals: number = 2): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
};

/**
 * 格式化时间戳为可读日期
 * 
 * @param timestamp 时间戳（Unix时间戳，秒或毫秒）
 * @returns 格式化后的日期字符串
 */
export const formatDate = (timestamp: number): string => {
  // 确保时间戳是毫秒
  const milliseconds = timestamp > 10000000000 ? timestamp : timestamp * 1000;
  const date = new Date(milliseconds);
  
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * 格式化时间戳为本地字符串
 * @param timestamp 时间戳(毫秒)
 * @returns 格式化后的日期字符串
 */
export const formatTimestamp = (timestamp: number): string => {
  return formatDate(timestamp);
}; 
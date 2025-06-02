// Monaco Editor Worker 配置
// 这个文件帮助 Monaco Editor 正确加载 worker 文件

self.MonacoEnvironment = {
  getWorkerUrl: function (moduleId, label) {
    if (label === 'json') {
      return './monaco-editor/min/vs/language/json/jsonWorker.js';
    }
    if (label === 'css' || label === 'scss' || label === 'less') {
      return './monaco-editor/min/vs/language/css/cssWorker.js';
    }
    if (label === 'html' || label === 'handlebars' || label === 'razor') {
      return './monaco-editor/min/vs/language/html/htmlWorker.js';
    }
    if (label === 'typescript' || label === 'javascript') {
      return './monaco-editor/min/vs/language/typescript/tsWorker.js';
    }
    return './monaco-editor/min/vs/editor/editor.worker.js';
  }
}; 
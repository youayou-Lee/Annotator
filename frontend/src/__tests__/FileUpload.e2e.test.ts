import { test, expect } from '@playwright/test';

// 文件上传的端到端测试
test.describe('文件上传功能', () => {
  test.beforeEach(async ({ page }) => {
    // 假设用户已登录并导航到文档上传页面
    await page.goto('/login');
    await page.fill('input[placeholder="Username/Email"]', 'admin');
    await page.fill('input[placeholder="Password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/');
    await page.click('a[href="/documents"]');
    await page.waitForURL('/documents');
  });

  test('上传有效文件并验证成功', async ({ page }) => {
    // 准备测试数据 - JSON文件
    const validJsonContent = JSON.stringify({ 
      name: "测试文档", 
      createdAt: "2023-05-01", 
      fields: ["字段1", "字段2"] 
    });
    
    // 等待上传组件加载
    await page.waitForSelector('input[type="file"]');
    
    // 模拟文件上传
    await page.setInputFiles('input[type="file"]', {
      name: 'valid-document.json',
      mimeType: 'application/json',
      buffer: Buffer.from(validJsonContent),
    });
    
    // 等待上传和校验完成
    await page.waitForSelector('text=校验通过', { timeout: 10000 });
    
    // 验证成功提示显示
    await expect(page.locator('text=上传成功')).toBeVisible();
    await expect(page.locator('text=文件已成功上传并通过校验')).toBeVisible();
    
    // 验证有"前往任务管理"链接
    await expect(page.locator('a:has-text("前往任务管理")')).toBeVisible();
  });
  
  test('上传无效文件并验证失败', async ({ page }) => {
    // 准备测试数据 - 格式错误的JSON文件
    const invalidJsonContent = '{ "name": "测试文档", createdAt: 错误的JSON }';
    
    // 等待上传组件加载
    await page.waitForSelector('input[type="file"]');
    
    // 模拟文件上传
    await page.setInputFiles('input[type="file"]', {
      name: 'invalid-document.json',
      mimeType: 'application/json',
      buffer: Buffer.from(invalidJsonContent),
    });
    
    // 等待校验完成
    await page.waitForSelector('text=校验失败', { timeout: 10000 });
    
    // 验证错误信息显示
    await expect(page.locator('text=错误详情')).toBeVisible();
    await expect(page.locator('li')).toContainText('JSON格式错误');
  });
  
  test('尝试上传不支持的文件格式', async ({ page }) => {
    // 等待上传组件加载
    await page.waitForSelector('input[type="file"]');
    
    // 模拟上传不支持的文件格式
    await page.setInputFiles('input[type="file"]', {
      name: 'document.txt',
      mimeType: 'text/plain',
      buffer: Buffer.from('这是一个文本文件'),
    });
    
    // 验证错误信息显示
    await expect(page.locator('text=只支持')).toBeVisible();
    await expect(page.locator('text=错误')).toBeVisible();
  });
  
  test('测试文件格式选择功能', async ({ page }) => {
    // 等待选择框加载
    await page.waitForSelector('span.ant-select-selection-item');
    
    // 点击选择框
    await page.click('span.ant-select-selection-item');
    
    // 选择CSV格式
    await page.click('div.ant-select-item-option[title="CSV"]');
    
    // 验证选择已更改
    await expect(page.locator('span.ant-select-selection-item')).toHaveText('CSV');
  });
}); 
# ǰ�������ű�

# �л���ǰ��Ŀ¼
Set-Location "$PSScriptRoot\frontend"

# ���û������������� CJS ����
$env:NODE_OPTIONS="--no-warnings"

# ����ǰ�˷���
Write-Host "��������ǰ�˷���..." -ForegroundColor Green
Write-Host "ǰ�˷����ַ: http://localhost:3000" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Green

# ִ��ǰ����������
npm run dev 
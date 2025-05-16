# ��������ű�

# ���� Conda ����
Write-Host "���ڼ��� Conda ���� (annotator)..." -ForegroundColor Yellow
conda activate annotator

# ��� Conda �����Ƿ񼤻�ɹ�
if ($LASTEXITCODE -ne 0) {
    Write-Host "�����޷����� Conda ��������ȷ���Ѱ�װ Conda �������� 'annotator' ����" -ForegroundColor Red
}

# �л������Ŀ¼
Set-Location "$PSScriptRoot\backend"

# ������˷���
Write-Host "����������˷���..." -ForegroundColor Green
Write-Host "��˷����ַ: http://localhost:8000" -ForegroundColor Cyan
Write-Host "�� Ctrl+C ����ֹͣ����" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Green

# ִ�к����������
uvicorn app.main:app --reload 
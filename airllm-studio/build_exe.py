import PyInstaller.__main__
import os
import shutil

# Önceki buildleri temizle
if os.path.exists('dist'):
    shutil.rmtree('dist')
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('AirLLM_Studio.spec'):
    os.remove('AirLLM_Studio.spec')

print("🚀 AirLLM Studio EXE paketleniyor...")

PyInstaller.__main__.run([
    'backend/app.py',
    '--name=AirLLM_Studio',
    '--onefile',
    '--windowed',  # Konsol penceresini gizle (isteğe bağlı, debug için kaldırılabilir)
    '--add-data=frontend;frontend',  # Frontend klasörünü dahil et
    '--hidden-import=flask',
    '--hidden-import=transformers',
    '--hidden-import=torch',
    '--hidden-import=accelerate',
    '--icon=NONE',  # İsterseniz buraya .ico dosyası yolu verebilirsiniz
    '--clean',
    '--noconfirm'
])

print("\n✅ İşlem Tamam!")
print("📦 Oluşturulan EXE dosyası: dist/AirLLM_Studio.exe")
print("\n💡 Not: İlk çalıştırmada model indirme işlemi internet hızınıza göre zaman alabilir.")

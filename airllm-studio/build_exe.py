# PyInstaller ile EXE Oluşturma Scripti
# Bu script, AirLLM Studio'yu tek bir .exe dosyasına dönüştürür.

import PyInstaller.__main__
import os
import shutil

# Proje kök dizini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Önceki build kalıntılarını temizle
for folder in ['build', 'dist']:
    path = os.path.join(BASE_DIR, folder)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"🧹 {folder} klasörü temizlendi.")

spec_file = os.path.join(BASE_DIR, 'AirLLM_Studio.spec')
if os.path.exists(spec_file):
    os.remove(spec_file)
    print("🧹 Eski .spec dosyası temizlendi.")

print("\n🚀 AirLLM Studio EXE paketleniyor...\n")

PyInstaller.__main__.run([
    'main.py',
    '--name=AirLLM_Studio',
    '--onefile',
    '--windowed',  # Konsol penceresini gizle (GUI uygulaması gibi)
    '--icon=NONE',  # İsterseniz .ico dosyası ekleyebilirsiniz
    '--add-data=frontend;frontend',  # Frontend klasörünü dahil et
    '--hidden-import=flask',
    '--hidden-import=werkzeug',
    '--hidden-import=torch',
    '--hidden-import=transformers',
    '--hidden-import=accelerate',
    '--collect-all=transformers',
    '--collect-all=accelerate',
    '--clean',  # Önbelleği temizle
    '--noconfirm',  # Onay sorma
])

print("\n✅ Paketleme tamamlandı!")
print("📦 EXE dosyası: dist/AirLLM_Studio.exe")
print("\n⚠️ NOT: İlk çalıştırmada model indirme işlemi olabilir.")

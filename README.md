## Cara Menjalankan Project Akhir ini 💻

### Menjalankan Jupyter Notebook

Untuk menjalankan analisis pada notebook Jupyter:

1. Masuk ke direktori project
   ```bash
   cd proyek_analisis_data
   pipenv install
   pipenv shell
   ```
2. Pastikan dependensi sudah terpasang menggunakan `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. Buka Jupyter Notebook:
   ```bash
   jupyter notebook Notebook_Navy.ipynb
   ```

### Menjalankan Dashboard Streamlit

Untuk menjalankan dasbor interaktif melalui lokal:

1. Instal semua dependensi jika belum dilakukan:
   ```bash
   pip install -r requirements.txt
   ```
2. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run dashboard/dashboard.py
   ```
Untuk menjalankan dashboard secara online:

https://projectdataanalysis-jviotazfbu82sugh9bwzdv.streamlit.app/

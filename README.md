Aktifkan Virtual Environment & Install Dependensi:   DOS
python -m venv myvenv
myvenv\Scripts\activate.bat
pip install celery flower requests
Jalankan Celery Worker:   DOS
set PYTHONPATH=.
celery -A celery_app worker -P solo -l info -Q fanout.log_system,fanout.notif_telegram,topic.http_check,topic.db_check,wild.all_http,wild.critical_alerts,default
Jalankan Producer (Input Generator):   DOS
python producer.py fanout --count 4
python producer.py topic --count 4
python producer.py wildcard --count 6
python producer.py pipeline
Jalankan Flower Monitoring (Opsional):   DOS
celery -A celery_app flower
Buka http://localhost:5555 di browser untuk memperlihatkan antrean tugas secara grafik.   


celery -A celery_app purge -f
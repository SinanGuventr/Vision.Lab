# Vision.Lab

Basit bir komut satırı laboratuvar takip programı. Numuneleri, deneyleri ve sonuç kayıtlarını yerel `lab_data.json` dosyasında saklar.

## Hızlı başlangıç

```bash
python lab_app.py init
python lab_app.py add-sample "DNA Örneği" "Genetik" "Dr. Ada"
python lab_app.py add-experiment "PCR" "Örnek DNA doğrulama" "Dr. Ada" --scheduled-for "2024-05-01 10:00"
python lab_app.py record-result 1 1 "başarı" "Amplifikasyon başarılı"
python lab_app.py list-samples
python lab_app.py list-experiments
python lab_app.py list-results
```

## Komutlar
- `init`: Boş bir veri dosyası oluşturur.
- `add-sample <isim> <kategori> <sorumlu>`: Numune ekler.
- `add-experiment <isim> <açıklama> <sorumlu> [--scheduled-for "TARİH"]`: Deney ekler.
- `record-result <deneyId> <numuneId> <durum> <not>`: Sonuç kaydeder.
- `list-samples`: Numuneleri listeler.
- `list-experiments [--lead <sorumlu>]`: Deneyleri listeler.
- `list-results [--status <durum>]`: Sonuçları listeler.

Varsayılan veri dosyası `lab_data.json` olup `--path` ile farklı bir konum verilebilir.

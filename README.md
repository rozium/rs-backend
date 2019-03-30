# rs-backend
Rumah Sahaja Backend

Cara make API

inisialisasi database dulu:
1. masuk ke console python3 di repo project
```
> python3
```
2. masukin command
```
> from rs import db

# buat inisialisasi tabel2
> db.create_all()

# buat ngehapus semua kolom (barangkali pengen ganti skema tabel, hapus dulu terus bikin lagi)
> db.drop_all()
```
Abis itu baru bisa dipake APInya

endpoint sesuaiin sama tabel
untuk create ama update masukkin data JSON di body

1. create: POST /endpoint
2. get data: GET /endpoint
3. update: PUT /endpoint
4. delete: DELETE /endpoint/:id

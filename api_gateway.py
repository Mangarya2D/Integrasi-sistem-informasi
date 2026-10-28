
from flask import Flask, request, jsonify
from pathlib import Path

app = Flask(__name__)

# Lokasi data.txt selalu mengikuti lokasi file api_gateway.py
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data.txt"

REQUIRED_FIELDS = ["id", "nama", "prodi", "status"]


def read_students():
    students = []

    if not DATA_FILE.exists():
        return students

    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            parts = line.split("|")

            # Abaikan baris dengan format yang tidak sesuai
            if len(parts) != 4:
                continue

            students.append({
                "id": parts[0],
                "nama": parts[1],
                "prodi": parts[2],
                "status": parts[3]
            })

    return students


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "API Gateway Mahasiswa aktif",
        "endpoints": {
            "GET": "/api/v1/students",
            "POST": "/api/v1/students"
        }
    }), 200


@app.route("/api/v1/students", methods=["GET"])
def get_students():
    return jsonify(read_students()), 200


@app.route("/api/v1/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    # Pastikan body berupa objek JSON
    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body harus berupa objek JSON"
        }), 400

    # Validasi field wajib
    missing_fields = [
        field for field in REQUIRED_FIELDS
        if not isinstance(data.get(field), str)
        or not data[field].strip()
    ]

    if missing_fields:
        return jsonify({
            "error": "Field wajib belum lengkap atau kosong",
            "missing_fields": missing_fields
        }), 422

    # Bersihkan spasi di awal dan akhir nilai
    new_student = {
        field: data[field].strip()
        for field in REQUIRED_FIELDS
    }

    # Karakter | tidak boleh digunakan karena menjadi pemisah data.txt
    if any("|" in value or "\n" in value or "\r" in value
           for value in new_student.values()):
        return jsonify({
            "error": "Field tidak boleh mengandung karakter | atau baris baru"
        }), 400

    students = read_students()

    # Tolak ID yang sudah terdaftar
    for student in students:
        if student["id"] == new_student["id"]:
            return jsonify({
                "error": "ID mahasiswa sudah terdaftar"
            }), 409

    # Tambahkan data ke file teks
    with DATA_FILE.open("a", encoding="utf-8") as file:
        file.write(
            f'{new_student["id"]}|'
            f'{new_student["nama"]}|'
            f'{new_student["prodi"]}|'
            f'{new_student["status"]}\n'
        )

    return jsonify({
        "message": "Mahasiswa berhasil ditambahkan",
        "data": new_student
    }), 201


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)


import json
import xml.etree.ElementTree as ET


def generate_mock_data(count):
    """Membuat data mahasiswa tiruan."""
    dataset = []

    for i in range(count):
        nomor = 1001 + i

        dataset.append({
            "id": str(nomor),
            "nama": f"Mahasiswa Integrasi Nomor {nomor}",
            "jurusan": "Sistem Informasi Enterprise",
            "status": "Aktif" if i % 2 == 0 else "Cuti"
        })

    return dataset


def serialize_json(dataset):
    """Serialisasi data ke JSON."""
    return json.dumps(
        {"data": dataset},
        ensure_ascii=False
    ).encode("utf-8")


def serialize_xml(dataset):
    """Serialisasi data ke XML."""
    root = ET.Element("response")
    students = ET.SubElement(root, "students")

    for student in dataset:
        student_element = ET.SubElement(students, "student")

        for key, value in student.items():
            field = ET.SubElement(student_element, key)
            field.text = value

    return ET.tostring(
        root,
        encoding="utf-8",
        xml_declaration=True
    )


def benchmark():
    record_counts = [10, 50, 100, 500]

    print("=" * 72)
    print("BENCHMARK SERIALISASI JSON VS XML")
    print("=" * 72)
    print(
        f"{'Records':>8} | {'JSON (bytes)':>14} | "
        f"{'XML (bytes)':>12} | {'Reduksi JSON (%)':>18}"
    )
    print("-" * 72)

    for count in record_counts:
        dataset = generate_mock_data(count)

        json_bytes = serialize_json(dataset)
        xml_bytes = serialize_xml(dataset)

        json_size = len(json_bytes)
        xml_size = len(xml_bytes)

        reduction = (
            (xml_size - json_size) / xml_size * 100
            if xml_size > 0 else 0
        )

        print(
            f"{count:>8} | {json_size:>14} | "
            f"{xml_size:>12} | {reduction:>17.2f}%"
        )

    print("-" * 72)
    print("Benchmark selesai.")


if __name__ == "__main__":
    benchmark()

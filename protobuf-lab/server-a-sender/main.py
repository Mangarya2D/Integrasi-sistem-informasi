import time
import grpc

import exchange_pb2
import exchange_pb2_grpc


def run():
    channel = grpc.insecure_channel("receiver-container:50051")
    stub = exchange_pb2_grpc.ExchangeServiceStub(channel)
    print("=== SERVER A: PENGIRIM DATA PROTOBUF ===")
    print("Ketik 'exit' pada bagian NIM untuk keluar.\n")

    while True:
        input_id = input("Masukkan NIM Mahasiswa: ")

        if input_id.strip().lower() == "exit":
            print("Server A berhenti. Sampai jumpa!")
            break

        input_name = input("Masukkan Nama Mahasiswa: ")
        start_time = time.time_ns()

        student_data = exchange_pb2.StudentRequest(
            student_id=input_id,
            student_name=input_name,
            sent_timestamp_ns=start_time
        )

        payload_size_bytes = student_data.ByteSize()
        print(f"Ukuran data: {payload_size_bytes} bytes")
        print("Mengirim data ke Server B...")

        try:
            response = stub.SendData(student_data, timeout=10)

            if response.status:
                print("Konfirmasi diterima dari Server B.\n")
            else:
                print("Server B tidak mengonfirmasi data.\n")

        except grpc.RpcError as e:
            print(f"Koneksi gagal: {e}\n")
            break

    channel.close()


if __name__ == "__main__":
    run()

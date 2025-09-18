import grpc
import booking_pb2
import booking_pb2_grpc

def run():
    """
    Запуск клиента и выполнение запроса
    """
    # Устанавливаем соединение с сервером
    with grpc.insecure_channel('localhost:50051') as channel:
        # Создаем stub (заглушку) для вызова удаленных методов
        stub = booking_pb2_grpc.BookingServiceStub(channel)

        # Запрашиваем данные у пользователя
        hotel_id = input("Введите ID отеля (например, hotel_paris): ").strip()
        room_id = input("Введите ID номера (например, room_101): ").strip()

        # Создаем запрос
        request = booking_pb2.BookingRequest(hotel_id=hotel_id, room_id=room_id)

        print(f"\n--- Запрос к серверу: доступность номера {room_id} в отеле {hotel_id} ---")
        try:
            # Вызываем удаленный метод и получаем ответ
            response = stub.CheckAvailability(request)

            # Обрабатываем ответ
            print(f"Ответ сервера: {response.message}")
            print(f"Доступен сейчас: {'Да' if response.available else 'Нет'}")

            if response.booked_slots:
                print("\nНомер занят в следующие периоды:")
                for i, slot in enumerate(response.booked_slots, 1):
                    print(f"  {i}. с {slot.start_time} по {slot.end_time}")
            else:
                print("\nАктивных броней нет.")

        except grpc.RpcError as e:
            print(f"Ошибка при вызове RPC: {e.code()}: {e.details()}")

if __name__ == '__main__':
    run()
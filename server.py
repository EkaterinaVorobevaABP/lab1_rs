import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import datetime

class BookingServicer(booking_pb2_grpc.BookingServiceServicer):
    """
    Реализация сервиса бронирования
    """

    # В реальном приложении эти данные брались бы из базы данных.
    # Здесь это просто примерная имитация.
    _existing_bookings = {
        "hotel_paris": { # hotel_id
            "room_101": [ # room_id
                # Список броней для номера 101 в парижском отеле
                {
                    "start": "2024-05-20T14:00:00Z",
                    "end": "2024-05-25T11:00:00Z"
                },
                {
                    "start": "2024-06-01T12:00:00Z",
                    "end": "2024-06-05T10:00:00Z"
                }
            ],
            "room_102": [] # Номер 102 свободен всегда
        },
        "hotel_rome": { # hotel_id
            "room_201": [ # room_id
                {
                    "start": "2024-05-15T00:00:00Z",
                    "end": "2024-05-18T00:00:00Z"
                }
            ]
        }
    }

    def CheckAvailability(self, request, context):
        """
        Реализация метода CheckAvailability.
        """
        hotel_id = request.hotel_id
        room_id = request.room_id

        print(f"Получен запрос на проверку доступности. Отель: '{hotel_id}', Номер: '{room_id}'")

        # Проверяем, знаем ли мы про такой отель и номер
        if hotel_id not in self._existing_bookings:
            return booking_pb2.AvailabilityResponse(
                available=False,
                message=f"Отель с ID '{hotel_id}' не найден.",
                booked_slots=[]
            )

        if room_id not in self._existing_bookings[hotel_id]:
            return booking_pb2.AvailabilityResponse(
                available=False,
                message=f"Номер с ID '{room_id}' не найден в отеле '{hotel_id}'.",
                booked_slots=[]
            )

        # Получаем список текущих броней для этого номера
        bookings_for_room = self._existing_bookings[hotel_id][room_id]

        # Преобразуем список броней в формат для ответа
        booked_slots = []
        for booking in bookings_for_room:
            # Создаем объект TimeSlot для каждой брони
            time_slot = booking_pb2.TimeSlot(
                start_time=booking["start"],
                end_time=booking["end"]
            )
            booked_slots.append(time_slot)

        # Проверяем, свободен ли номер ПРЯМО СЕЙЧАС.
        # В реальной системе здесь была бы более сложная логика,
        # например, проверка на пересечение с желаемыми датами клиента.
        is_available_now = (len(bookings_for_room) == 0)

        if is_available_now:
            response_message = f"Номер {room_id} в отеле {hotel_id} свободен."
        else:
            response_message = f"Номер {room_id} в отеле {hotel_id} занят. Смотрите список броней."

        # Формируем и возвращаем ответ
        return booking_pb2.AvailabilityResponse(
            available=is_available_now,
            message=response_message,
            booked_slots=booked_slots
        )

def serve():
    """
    Запуск gRPC сервера
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServiceServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Сервер бронирования запущен на порту 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
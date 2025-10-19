using Microsoft.Extensions.Configuration;
using RobotParkClient.Models;
using RobotParkClient.Services;

var config = new ConfigurationBuilder()
    .SetBasePath(Directory.GetCurrentDirectory())
    .AddJsonFile("appsettings.json")
    .Build();

var baseUrl = config["ApiBaseUrl"] ?? "http://localhost:5000";
var api = new ApiService(baseUrl);

while (true)
{
    Console.WriteLine("\n=== Менеджер парка роботов ===");
    Console.WriteLine("1. Список роботов");
    Console.WriteLine("2. Добавить робота");
    Console.WriteLine("3. Добавить тип миссии");
    Console.WriteLine("4. Запланировать миссию");
    Console.WriteLine("5. Список миссий");
    Console.WriteLine("6. Обновить статус миссии");
    Console.WriteLine("7. Показать месячный отчёт");
    Console.WriteLine("0. Выход");
    Console.Write("Выберите действие: ");

    var choice = Console.ReadLine();
    try
    {
        switch (choice)
        {
            case "1":
                var robots = await api.GetRobotsAsync();
                foreach (var r in robots) Console.WriteLine($"[{r.Id}] {r.Name} ({r.Type}) - {r.Status}");
                break;

            case "2":
                Console.Write("Имя: "); var name = Console.ReadLine()!;
                Console.Write("Модель: "); var model = Console.ReadLine()!;
                Console.Write("Тип (ground/aerial/marine): "); var type = Console.ReadLine()!;
                Console.Write("Серийный номер: "); var sn = Console.ReadLine()!;
                await api.CreateRobotAsync(new Robot { Name = name, Model = model, Type = type, SerialNumber = sn });
                Console.WriteLine("Робот создан");
                break;

            case "3":
                Console.Write("Название типа миссии: "); var mtName = Console.ReadLine()!;
                await api.CreateMissionTypeAsync(new MissionType { Name = mtName });
                Console.WriteLine("Тип миссии создан");
                break;

            case "4":
                Console.Write("ID робота: "); var robotId = int.Parse(Console.ReadLine()!);
                Console.Write("ID типа миссии: "); var mtId = int.Parse(Console.ReadLine()!);
                Console.Write("Название миссии: "); var title = Console.ReadLine()!;
                Console.Write("Время начала (YYYY-MM-DD HH:mm, или Enter для null): ");
                var startInput = Console.ReadLine();
                DateTime? startTime = string.IsNullOrWhiteSpace(startInput) ? null : DateTime.Parse(startInput);
                await api.CreateMissionAsync(new Mission
                {
                    RobotId = robotId,
                    MissionTypeId = mtId,
                    Title = title,
                    StartTime = startTime
                });
                Console.WriteLine("Миссия запланирована");
                break;

            case "5":
                Console.Write("Фильтр по статусу (Enter — без фильтра): ");
                var statusFilter = Console.ReadLine();
                
                Console.Write("Фильтр по дате начала (YYYY-MM-DD, Enter — без фильтра): ");
                var dateFromInput = Console.ReadLine();

                DateTime? dateFrom = string.IsNullOrEmpty(dateFromInput) ? null : DateTime.Parse(dateFromInput);

                var missions = await api.GetMissionsAsync(status: string.IsNullOrEmpty(statusFilter) ? null : statusFilter, dateFrom: dateFrom);

                foreach (var m in missions)
                    Console.WriteLine($"[{m.Id}] {m.Title} — {m.Status} ({m.StartTime?.ToString("g")})");
                break;

            case "6":
                Console.Write("ID миссии: "); var missionId = int.Parse(Console.ReadLine()!);
                Console.Write("Новый статус: "); var newStatus = Console.ReadLine()!;
                Console.Write("Время окончания (YYYY-MM-DD HH:mm): "); var endTimeStr = Console.ReadLine()!;
                Console.Write("Пройденное расстояние (м): "); var dist = decimal.Parse(Console.ReadLine()!);
                await api.UpdateMissionAsync(missionId, new
                {
                    status = newStatus,
                    end_time = DateTime.Parse(endTimeStr),
                    distance_meters = dist
                });
                Console.WriteLine("Миссия обновлена");
                break;

            case "7":
                Console.Write("Год (напр. 2025): "); var year = int.Parse(Console.ReadLine()!);
                Console.Write("Месяц (1–12): "); var month = int.Parse(Console.ReadLine()!);
                var report = await api.GetMonthlyReportAsync(year, month);
                Console.WriteLine($"\nОтчёт за {report.Month}");
                Console.WriteLine($"Всего миссий: {report.TotalMissions}");
                Console.WriteLine($"Завершено: {report.Completed}, Неудач: {report.Failed}, В работе: {report.InProgress}");
                Console.WriteLine($"Общее расстояние: {report.TotalDistanceM} м");
                break;

            case "0":
                return;

            default:
                Console.WriteLine("Неверный выбор.");
                break;
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Ошибка: {ex.Message}");
    }
}
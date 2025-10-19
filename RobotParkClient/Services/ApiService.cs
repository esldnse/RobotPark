using System.Text;
using System.Text.Json;
using RobotParkClient.Models;

namespace RobotParkClient.Services;

public class ApiService
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    };

    public ApiService(string baseUrl)
    {
        _httpClient = new HttpClient();
        _baseUrl = baseUrl.TrimEnd('/');
    }

    private async Task<T?> GetAsync<T>(string endpoint)
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}{endpoint}");
        await HandleResponse(response);
        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(json, JsonOptions);
    }

    private async Task<T?> PostAsync<T>(string endpoint, object data)
    {
        var json = JsonSerializer.Serialize(data, JsonOptions);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        var response = await _httpClient.PostAsync($"{_baseUrl}{endpoint}", content);
        await HandleResponse(response);
        var responseJson = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(responseJson, new JsonSerializerOptions { PropertyNameCaseInsensitive = true });
    }

    private async Task PatchAsync(string endpoint, object data)
    {
        var json = JsonSerializer.Serialize(data);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        using var request = new HttpRequestMessage(new HttpMethod("PATCH"), $"{_baseUrl}{endpoint}")
        {
            Content = content
        };
        var response = await _httpClient.SendAsync(request);
        await HandleResponse(response);
    }

    private async Task DeleteAsync(string endpoint)
    {
        var response = await _httpClient.DeleteAsync($"{_baseUrl}{endpoint}");
        await HandleResponse(response);
    }

    private static async Task HandleResponse(HttpResponseMessage response)
    {
        if (!response.IsSuccessStatusCode)
        {
            var errorContent = await response.Content.ReadAsStringAsync();
            try
            {
                using var doc = JsonDocument.Parse(errorContent);
                if (doc.RootElement.TryGetProperty("error", out var errorProp))
                {
                    var message = errorProp.GetString() ?? "Unknown error";
                    Console.WriteLine($"HTTP {response.StatusCode}: {message}");
                    throw new HttpRequestException($"API error: {message}");
                }
                else
                {
                    Console.WriteLine($"HTTP {response.StatusCode}: {errorContent}");
                    throw new HttpRequestException("API returned unexpected error format");
                }
            }
            catch (JsonException)
            {
                Console.WriteLine($"HTTP {response.StatusCode}: {errorContent}");
                throw new HttpRequestException("API returned non-JSON error");
            }
        }
    }

    public Task<List<Robot>> GetRobotsAsync(string? type = null, string? status = null)
    {
        var query = "";
        if (!string.IsNullOrEmpty(type) || !string.IsNullOrEmpty(status))
        {
            var parts = new List<string>();
            if (!string.IsNullOrEmpty(type)) parts.Add($"type={type}");
            if (!string.IsNullOrEmpty(status)) parts.Add($"status={status}");
            query = "?" + string.Join("&", parts);
        }
        return GetAsync<List<Robot>>($"/robots{query}");
    }

    public Task<Robot> CreateRobotAsync(Robot robot) => PostAsync<Robot>("/robots", robot);
    public Task<Robot> GetRobotAsync(int id) => GetAsync<Robot>($"/robots/{id}");
    public Task UpdateRobotAsync(int id, object updateData) => PatchAsync($"/robots/{id}", updateData);
    public Task DeleteRobotAsync(int id) => DeleteAsync($"/robots/{id}");

    public Task<List<MissionType>> GetMissionTypesAsync() => GetAsync<List<MissionType>>("/mission_types");
    public Task<MissionType> CreateMissionTypeAsync(MissionType mt) => PostAsync<MissionType>("/mission_types", mt);
    public Task DeleteMissionTypeAsync(int id) => DeleteAsync($"/mission_types/{id}");

    public Task<List<Mission>> GetMissionsAsync(
        int? robotId = null,
        int? missionTypeId = null,
        string? status = null,
        DateTime? dateFrom = null,
        DateTime? dateTo = null)
    {
        var parts = new List<string>();
        if (robotId.HasValue) parts.Add($"robot_id={robotId}");
        if (missionTypeId.HasValue) parts.Add($"mission_type_id={missionTypeId}");
        if (!string.IsNullOrEmpty(status)) parts.Add($"status={status}");
        if (dateFrom.HasValue) parts.Add($"date_from={dateFrom:yyyy-MM-ddTHH:mm:ss}");
        if (dateTo.HasValue) parts.Add($"date_to={dateTo:yyyy-MM-ddTHH:mm:ss}");
        var query = parts.Any() ? "?" + string.Join("&", parts) : "";
        return GetAsync<List<Mission>>($"/missions{query}");
    }

    public Task<Mission> CreateMissionAsync(Mission mission) => PostAsync<Mission>("/missions", mission);
    public Task<Mission> GetMissionAsync(int id) => GetAsync<Mission>($"/missions/{id}");
    public Task UpdateMissionAsync(int id, object updateData) => PatchAsync($"/missions/{id}", updateData);
    public Task DeleteMissionAsync(int id) => DeleteAsync($"/missions/{id}");

    public Task<MonthlyReport> GetMonthlyReportAsync(int year, int month)
        => GetAsync<MonthlyReport>($"/reports/monthly?year={year}&month={month:D2}");
}
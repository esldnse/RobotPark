using System.Text.Json.Serialization;

namespace RobotParkClient.Models;

public class MissionType
{
    [JsonIgnore]
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
}
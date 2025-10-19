namespace RobotParkClient.Models;

public class Mission
{
    public int Id { get; set; }
    public int RobotId { get; set; }
    public int MissionTypeId { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Status { get; set; } = "planned";
    public DateTime? StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public decimal? DistanceMeters { get; set; }
    public decimal? PayloadKg { get; set; }
    public string? Note { get; set; }
}
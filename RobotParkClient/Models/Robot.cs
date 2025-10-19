namespace RobotParkClient.Models;

public class Robot
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string Model { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public string SerialNumber { get; set; } = string.Empty;
    public string Status { get; set; } = "idle";
    public int BatteryLevel { get; set; } = 100;
}
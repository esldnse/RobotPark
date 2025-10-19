namespace RobotParkClient.Models;

public class MonthlyReport
{
    public string Month { get; set; } = string.Empty;
    public int TotalMissions { get; set; }
    public int Completed { get; set; }
    public int Failed { get; set; }
    public int InProgress { get; set; }
    public decimal TotalDistanceM { get; set; }

    public List<ByMissionType> ByMissionType { get; set; } = new();
    public List<ByRobot> ByRobot { get; set; } = new();
}

public class ByMissionType
{
    public string MissionType { get; set; } = string.Empty;
    public int Count { get; set; }
    public decimal DistanceM { get; set; }
}

public class ByRobot
{
    public int RobotId { get; set; }
    public string RobotName { get; set; } = string.Empty;
    public int Count { get; set; }
    public decimal DistanceM { get; set; }
}
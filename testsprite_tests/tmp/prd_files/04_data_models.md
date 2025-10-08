# Data Models

## Database Tables

### communications_suntech

Stores GPS communications from Suntech devices.

**Key Fields**:
- `id`: Primary key (integer)
- `device_id`: Device identifier (string, indexed)
- `latitude`: GPS latitude (numeric/decimal)
- `longitude`: GPS longitude (numeric/decimal)
- `speed`: Vehicle speed (numeric/decimal)
- `course`: Direction/heading (numeric/decimal)
- `gps_datetime`: GPS timestamp (datetime)
- `gps_epoch`: GPS timestamp in epoch format (bigint)
- `main_battery_voltage`: Main battery voltage (numeric)
- `backup_battery_voltage`: Backup battery voltage (numeric)
- `odometer`: Total odometer reading (bigint)
- `trip_distance`: Trip distance (bigint)
- `total_distance`: Total distance (bigint)
- `engine_status`: Engine on/off status (string)
- `fix_status`: GPS fix status (string)
- `network_status`: Network connection status (string)
- `received_at`: Server reception timestamp (datetime)
- `created_at`: Record creation timestamp (datetime)

### communications_queclink

Stores GPS communications from Queclink devices.

**Structure**: Same as communications_suntech (inherits from CommunicationBase)

## API Response Schema

**CommunicationResponse**:
```json
{
  "device_id": "string",
  "latitude": "number",
  "longitude": "number",
  "speed": "number",
  "course": "number",
  "gps_datetime": "datetime",
  "main_battery_voltage": "number",
  "backup_battery_voltage": "number",
  "odometer": "number",
  "trip_distance": "number",
  "total_distance": "number",
  "engine_status": "string",
  "fix_status": "string",
  "network_status": "string",
  "received_at": "datetime"
}
```

## Data Requirements

- All GPS coordinates must be valid latitude/longitude values
- Timestamps must be in ISO 8601 format
- Numeric fields can be null if data not available
- Device IDs are case-sensitive strings
- API must query both Suntech and Queclink tables and merge results


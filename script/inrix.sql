-- westbound: 3rd Ave, 7th Ave, 15th Ave, 19th Ave
SELECT t1.SegmentID, t2.Name, t1.Bearing, t1.Miles, t1.StartLat, t2.Latitude, t1.EndLat, t1.StartLong, t2.Longitude, t1.EndLong
FROM [ADOT_INRIX].[dbo].[InrixSegments_Geometry] AS t1
LEFT JOIN [ADOT_INRIX].[dbo].[InrixSegments] AS t2
ON t1.SegmentID = t2.ID
WHERE ID IN ('450124637', '450124638', '450124850', '450124851')
ORDER BY -Longitude

-- easbound: 19th Ave, 15th Ave, 7th Ave, 3rd Ave
SELECT t1.SegmentID, t2.Name, t1.Bearing, t1.Miles, t1.StartLat, t2.Latitude, t1.EndLat, t1.StartLong, t2.Longitude, t1.EndLong
FROM [ADOT_INRIX].[dbo].[InrixSegments_Geometry] AS t1
LEFT JOIN [ADOT_INRIX].[dbo].[InrixSegments] AS t2
ON t1.SegmentID = t2.ID
WHERE ID IN ('450124848', '450124849', '450124635', '450124636')
ORDER BY Longitude

-- speed data
SELECT timestamp, SegmentID, speed, score, travelTimeMinutes
FROM [ADOT_INRIX].[dbo].[Inrix_Realtime]
WHERE SegmentID IN ('450124637', '450124638', '450124850', '450124851') AND timestamp BETWEEN '2022-11-30 00:00:00' AND '2022-12-02 00:00:00'
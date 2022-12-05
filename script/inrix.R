library(RODBC)
library(data.table)
library(plotly)

source("ignore/keys.R")

am_peak <- c(6L, 7L, 8L)
pm_peak <- c(15L, 16L, 17L)

db_speed <- '[ADOT_INRIX].[dbo].[Inrix_Realtime]'

query <- paste0(
    "SELECT timestamp, SegmentID, speed, score, travelTimeMinutes FROM ", db_speed,
    " WHERE SegmentID IN ('450124637', '450124638', '450124850', '450124851') AND timestamp BETWEEN '2022-11-30 00:00:00' AND '2022-12-02 00:00:00'"
)

DT <- as.data.table(sqlQuery(getSQLConnection('STL5'), query))

DT[, timestamp := as.POSIXct(timestamp, format = '%Y-%m-%d %H:%M:%S') - 7*3600]
DT <- DT[wday(timestamp) == 5L & hour(timestamp) == 7L, ][order(timestamp)]

DT[, SegmentID := fcase(SegmentID == 450124637, 'Central-3rd',
                        SegmentID == 450124638, '3rd-7th',
                        SegmentID == 450124850, '7th-15th',
                        SegmentID == 450124851, '15th-19th')]

plot_ly(DT, type = 'scatter', x = ~timestamp, y = ~speed, color = ~SegmentID, mode = 'lines+markers')

plot_ly(DT, type = 'scatter', x = ~timestamp, y = ~travelTimeMinutes, color = ~SegmentID, mode = 'lines+markers')

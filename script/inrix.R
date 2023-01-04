library(RODBC)
library(data.table)
library(plotly)

source("ignore/keys.R")

db_speed <- '[ADOT_INRIX].[dbo].[Inrix_Realtime]'

seg_wb <- c('450124637', '450124638', '450124850', '450124851')
seg_wb <- paste(sQuote(seg_wb, "'"), collapse = ',')
seg_wb <- paste0("(", seg_wb, ")")

# time: 2022-12-14 8:00 - 8:15
query_wb <- paste0(
    "SELECT timestamp, SegmentID, speed, score, travelTimeMinutes FROM ", db_speed,
    " WHERE SegmentID IN ", seg_wb,
    " AND timestamp BETWEEN '2022-12-14 00:00:00' AND '2022-12-14 23:59:59'"
)

DT <- as.data.table(sqlQuery(getSQLConnection('STL5'), query_wb))

DT[, timestamp := as.POSIXct(timestamp, format = '%Y-%m-%d %H:%M:%S') - 7*3600]
DT <- DT[hour(timestamp) == 8L & minute(timestamp) <= 15L, ][order(timestamp)]

DT[, SegmentID := fcase(SegmentID == 450124637, 'Central-3rd',
                        SegmentID == 450124638, '3rd-7th',
                        SegmentID == 450124850, '7th-15th',
                        SegmentID == 450124851, '15th-19th')]

plot_ly(DT, type = 'box', y = ~speed, color = ~SegmentID, boxmean = TRUE)

plot_ly(DT, type = 'scatter', x = ~timestamp, y = ~speed, color = ~SegmentID, mode = 'lines+markers')

plot_ly(DT, type = 'scatter', x = ~timestamp, y = ~travelTimeMinutes, color = ~SegmentID, mode = 'lines+markers')

library(data.table)
library(ggplot2)
library(patchwork)
library(plotly)

data <- fread("ignore/Phoenix/20221122_CSVExport/20221122_CSVExport.txt")
data[, TimeStamp := as.POSIXct(TimeStamp, tz = '', format = '%m-%d-%Y %H:%M:%OS')]

options(digits.secs = 3L)

param_eb <- c(17, 18, 19, 20, 37, 38, 39, 40, 61, 62, 63, 64)
param_wb <- c(9, 10, 11, 12, 29, 30, 31, 32, 53, 54, 55, 56)
param_nb <- c(13, 14, 15, 16, 33, 34, 35, 36, 57, 58, 59, 60)
param_sb <- c(21, 22, 23, 24, 41, 42, 43, 44)

# # check detector configuration
# DT <- copy(data)[DeviceID == 49L & hour(TimeStamp) %in% c(6L, 7L, 8L) & Parameter %in% param_eb & EventID == 82L, ]
# DT[, .N, by = Parameter][order(Parameter)]

# check data continuity
DT_eb <- copy(data)[hour(TimeStamp) %in% c(6L, 7L, 8L) & Parameter %in% param_eb & EventID == 82L, ]
DT_wb <- copy(data)[hour(TimeStamp) %in% c(6L, 7L, 8L) & Parameter %in% param_wb & EventID == 82L, ]

p1 <- ggplot(DT_wb) + 
    geom_point(aes(TimeStamp, DeviceID)) + 
    theme(axis.text.x = element_blank(),
          axis.title.x = element_blank(),
          axis.ticks.x = element_blank())

p2 <- ggplot(DT_eb) + 
    geom_point(aes(TimeStamp, DeviceID))

p1 / p2

# process data
DT <- copy(data)[DeviceID == 46L & hour(TimeStamp) %in% c(7L) & minute(TimeStamp) <= 40, ]
DT <- DT[Parameter %in% c(2L, 9L, 10L, 11L, 12L), ][order(TimeStamp)]
DT$DeviceID <- NULL

DT <- DT[min(which(DT$EventID == 10L)):max(which(DT$EventID == 10L)), ]
DT <- DT[.(c(10L, 1L, 82L)), on = 'EventID'] # order data by EventID

DT[, Cycle := .I]
DT[, CycleLength := abs(round(TimeStamp - shift(TimeStamp, type = 'lead'), 3L))]
DT[Cycle >= max(which(DT$EventID == 10L)), `:=`(Cycle = NA, CycleLength = NA)]

DT <- DT[order(TimeStamp)][, setnafill(.SD, type = 'locf', cols = c('Cycle', 'CycleLength'))]

DT[, Cycle := as.factor(Cycle)]
DT[, TimeInCycle := as.numeric(abs(round(TimeStamp - shift(TimeStamp), 3L))), by = Cycle]
DT[, TimeInCycle := cumsum(fifelse(is.na(TimeInCycle), 0, TimeInCycle)), by = Cycle]
DT[, TimeInCycle := as.difftime(TimeInCycle, units = 'secs')]

DT[, GreenStart := TimeInCycle[EventID == 1L], by = Cycle]
DT[, DetTimeInCycle := fcase(EventID == 82L, TimeInCycle)]

plot_ly(DT, x = ~TimeStamp) |> 
    add_lines(y = ~CycleLength, line = list(shape = 'hv', color = 'red')) |> 
    add_lines(y = ~GreenStart, line = list(shape = 'hv', color = 'forestgreen')) |> 
    add_markers(y = ~DetTimeInCycle, marker = list(size = 3L, color = 'black')) |> 
    layout(showlegend = FALSE,
           xaxis = list(title = 'Time of Day'),
           yaxis = list(title = 'Time in Cycle (s)'))

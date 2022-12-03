library(data.table)
library(ggplot2)
library(patchwork)
library(plotly)

param_eb <- c(17, 18, 19, 20, 37, 38, 39, 40, 61, 62, 63, 64)
param_wb <- c(9, 10, 11, 12, 29, 30, 31, 32, 53, 54, 55, 56)
param_nb <- c(13, 14, 15, 16, 33, 34, 35, 36, 57, 58, 59, 60)
param_sb <- c(21, 22, 23, 24, 41, 42, 43, 44)

phase_eb <- 6L
phase_wb <- 2L

det_eb_stop <- c(17L, 18L, 19L, 20L)
det_wb_stop <- c(9L, 10L, 11L, 12L)
det_eb_advance <- c(37L, 38L, 39L, 40L)
det_wb_advance <- c(29L, 30L, 31L, 32L)

am_peak <- c(6L, 7L, 8L)
pm_peak <- c(15L, 16L, 17L)

folder_name <- '20221201_IndianSchool'
file_name <- paste0("ignore/Phoenix/", folder_name, '.txt')
data <- fread(file_name)
data[, TimeStamp := as.POSIXct(TimeStamp, tz = '', format = '%m-%d-%Y %H:%M:%OS')]

options(digits.secs = 3L)

# check detector configuration
DT <- copy(data)[hour(TimeStamp) %in% am_peak & Parameter %in% param_wb & EventID == 82L, ]
DT[, .N, by = c('DeviceID', 'Parameter')][order(DeviceID, Parameter)]

# check data continuity
DT_eb <- copy(data)[hour(TimeStamp) %in% am_peak & Parameter %in% param_eb & EventID == 82L, ]
DT_wb <- copy(data)[hour(TimeStamp) %in% am_peak & Parameter %in% param_wb & EventID == 82L, ]

p1 <- ggplot(DT_wb) + 
    geom_point(aes(TimeStamp, DeviceID)) + 
    theme(axis.text.x = element_blank(),
          axis.title.x = element_blank(),
          axis.ticks.x = element_blank())

p2 <- ggplot(DT_eb) + 
    geom_point(aes(TimeStamp, DeviceID))

p1 / p2


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Purdue Coordination Diagram --------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# process data

DT <- copy(data)[DeviceID == 49L & hour(TimeStamp) %in% c(7L) & minute(TimeStamp) <= 50, ]
DT$DeviceID <- NULL

DT <- DT[Parameter %in% c(phase_wb, det_wb_stop), ][order(TimeStamp)] # westbound
# DT <- DT[Parameter %in% c(6L, 17L, 18L, 19L, 20L), ][order(TimeStamp)] # eastbound

# remove observations with det event and phase parameter 
DT <- DT[!(EventID == 82L & Parameter == phase_wb), ]

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

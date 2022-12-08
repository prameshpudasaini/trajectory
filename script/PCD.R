library(data.table)
library(ggplot2)
library(patchwork)
library(plotly)

am_peak <- c(6L, 7L, 8L)
pm_peak <- c(15L, 16L, 17L)

# detector configuration for Indian School Rd
phase_eb <- 6L
phase_wb <- 2L

det_eb_stop <- c(17L, 18L, 19L)
det_eb_advance <- c(20L, 25L, 26L)

det_wb_stop <- c(9L, 10L, 11L, 12L)
det_wb_advance <- c(27L, 28L, 29L)

# read data
folder_name <- '20221207_IndianSchool'
file_name <- paste0("ignore/Phoenix/", folder_name, '.txt')
data <- fread(file_name)
data[, TimeStamp := as.POSIXct(TimeStamp, tz = '', format = '%m-%d-%Y %H:%M:%OS')]

options(digits.secs = 3L)

# convert Device ID
convertDevID <- function(x) {
    x[, DeviceID := factor(as.factor(fcase(DeviceID == 46, '19th Ave',
                                           DeviceID == 47, '15th Ave',
                                           DeviceID == 48, '7th Ave',
                                           DeviceID == 49, '3rd Ave')),
                           levels = c('19th Ave', '15th Ave', '7th Ave', '3rd Ave'))][]
    return(x)
}

# check detector configuration
checkDetConf <- function(peak, param, dir) {
    dt <- copy(data)[hour(TimeStamp) %in% peak & Parameter %in% param & EventID == 82L, ]
    dt <- dt[, .N, by = c('DeviceID', 'Parameter')][order(DeviceID, Parameter)]
    dt <- convertDevID(dt)
    dt[, DeviceID := paste0(DeviceID, ' ', dir)][]
    return(dt)
}

checkDetConf(am_peak, det_eb_stop, 'EB')
checkDetConf(am_peak, det_eb_advance, 'EB')

checkDetConf(am_peak, det_wb_stop, 'WB')
checkDetConf(am_peak, det_wb_advance, 'WB')

# check data continuity
checkDataCont <- function(peak, det_type) {
    
    if (det_type == 'stop') {
        param_eb <- det_eb_stop
        param_wb <- det_wb_stop
    } else {
        param_eb <- det_eb_advance
        param_wb <- det_wb_advance
    }
    
    dt_eb <- copy(data)[hour(TimeStamp) %in% peak & Parameter %in% param_eb & EventID == 82L, ]
    dt_eb <- convertDevID(dt_eb)
    
    dt_wb <- copy(data)[hour(TimeStamp) %in% peak & Parameter %in% param_wb & EventID == 82L, ]
    dt_wb <- convertDevID(dt_wb)
    
    p1 <- ggplot(dt_eb) + 
        geom_point(aes(TimeStamp, DeviceID)) + 
        ylab('Eastbound') + 
        theme(axis.title.x = element_blank())
    
    p2 <- ggplot(dt_wb) + 
        geom_point(aes(TimeStamp, DeviceID)) + 
        ylab('Westbound') + 
        theme(axis.title.x = element_blank())
    
    return(p2 / p1)
}

checkDataCont(am_peak, 'stop')


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Purdue Coordination Diagram --------------------------------------------------
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# process data
device <- 49L
hour <- 8L
minute <- 35L

DT <- copy(data)[DeviceID == device & hour(TimeStamp) %in% hour & minute(TimeStamp) <= minute, ]
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

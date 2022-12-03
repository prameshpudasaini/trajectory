library(data.table)
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

data <- data[DeviceID == 49L & hour(TimeStamp) %in% c(7L) & minute(TimeStamp) <= 50, ]
data$DeviceID <- NULL


# signal phase change events

seq_phase_event <- c(7L, 8L, 9L, 10L, 11L, 1L)

phase <- copy(data)[EventID %in% seq_phase_event & Parameter %in% phase_wb, ][order(TimeStamp)]
phase[, .N, by = EventID] # check

minCycleTime <- phase$TimeStamp[min(which(phase$EventID == 7L))]
maxCycleTime <- phase$TimeStamp[max(which(phase$EventID == 7L))]

phase <- phase[between(TimeStamp, minCycleTime, maxCycleTime), ]
phase <- phase[EventID %in% c(8L, 10L, 1L), ]

yellowStartTime <- phase$TimeStamp[phase$EventID == 8L]
redStartTime <- phase$TimeStamp[phase$EventID == 10L]
greenStartTime <- phase$TimeStamp[phase$EventID == 1L]

Cycle <- seq(1L, length(yellowStartTime))
CL <- round(as.numeric(difftime(shift(yellowStartTime, type = 'lead'), yellowStartTime, units = 'secs')), 3L)

GreenTime <- round(as.numeric(difftime(greenStartTime, head(yellowStartTime, -1L))), 3L)
GreenTime <- append(GreenTime, NA)


# detector actuation events

det <- copy(data)[EventID %in% c(82L, 81L) & Parameter %in% det_wb_stop, ][order(TimeStamp)]
det <- det[between(TimeStamp, minCycleTime, maxCycleTime), ][order(TimeStamp)]

det_dir_loc <- unique(det$Parameter)

# get detection parameters for each lane-by-lane detector
getOHG <- function(det_lane) {
    det1 <- copy(det)[Parameter == det_lane, ]
    det1 <- det1[min(which(EventID == 82L)):max(which(EventID == 81L)), ]
    
    detOn <- det1$TimeStamp[det1$EventID == 82L]
    detOff <- det1$TimeStamp[det1$EventID == 81L]
    
    Headway <- round(as.numeric(difftime(shift(detOn, type = 'lead'), detOn, units = 'secs')), 3L)
    ODT <- round(as.numeric(difftime(detOff, detOn, units = 'secs')), 3L)
    Gap <- round(as.numeric(difftime(shift(detOn, type = 'lead'), detOff, units = 'secs')), 3L)
    
    return(list(Headway = Headway, ODT = ODT, Gap = Gap))
}


# merge two events data sets

DT <- rbindlist(list(phase, det))[order(TimeStamp)]

DT[, Signal := fifelse(EventID %in% c(8L, 10L, 1L), EventID, as.integer(NA))]
DT <- DT[, setnafill(.SD, type = 'locf', cols = 'Signal')]

DT[, Signal := factor(as.factor(fcase(Signal == 1L, 'G',
                                      Signal == 8L, 'Y',
                                      Signal == 10L, 'R')), levels = c('G', 'Y', 'R'))]

DT$Cycle[DT$EventID == 8L] <- Cycle
DT$CL[DT$EventID == 8L] <- CL

DT$YellowStart[DT$EventID == 8L] <- yellowStartTime
DT$RedStart[DT$EventID == 8L] <- append(redStartTime, NA)
DT$GreenStart[DT$EventID == 8L] <- append(greenStartTime, NA)
DT$GreenTime[DT$EventID == 8L] <- GreenTime

DT <- DT[, setnafill(.SD, type = 'locf', cols = c('Cycle', 'CL', 'GreenStart', 'YellowStart', 'RedStart', 'GreenTime'))]

origin <- '1970-01-01'
DT[, YellowStart := as.POSIXct(YellowStart, origin = origin)]
DT[, RedStart := as.POSIXct(RedStart, origin = origin)]
DT[, GreenStart := as.POSIXct(GreenStart, origin = origin)]

DT[, AIC := round(as.numeric(TimeStamp - YellowStart), 3L)]
DT[, TUG := round(as.numeric(GreenStart - TimeStamp), 3L)]

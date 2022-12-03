library(data.table)

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

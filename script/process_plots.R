library(data.table)
library(plotly)

# read data
folder_name <- 'output/20221214_ISR'
file_name <- 'wb_3rd_stop'
path <- paste0(folder_name, '/', file_name, '.txt')

DT <- fread(path)[order(TimeStamp)]
DT$EventID <- NULL

SSC_levels <- c('YY', 'YR', 'RR', 'RG', 'GG', 'GY')
DT[, SSC := factor(as.factor(SSC), levels = SSC_levels)]

summary_SSC <- DT[, .(count = .N, 
       min_ODT = min(ODT),
       max_ODT = max(ODT),
       mean_ODT = round(mean(ODT), 3L),
       median_ODT = median(ODT), 
       sd_ODT = round(sd(ODT), 4L)), by = c('SSC', 'Parameter')][order(SSC, Parameter)]
summary_SSC

det_dir_loc <- sort(unique(DT$Parameter))
det_dir_loc

exclude_SRT <- TRUE

if (exclude_SRT == TRUE) {
    DT <- DT[Parameter != det_dir_loc[1], ]
}

summary_SSC <- DT[, .(count = .N, 
                      min_ODT = min(ODT),
                      max_ODT = max(ODT),
                      mean_ODT = round(mean(ODT), 3L),
                      median_ODT = median(ODT), 
                      sd_ODT = round(sd(ODT), 4L)), by = c('SSC', 'Parameter')][order(SSC, Parameter)]
summary_SSC

DT[, TUG := fifelse(SSC %in% c('GG', 'GY'), 0L, TUG)]
DT[, Parameter := as.factor(Parameter)]

levels(DT$SSC)
levels(DT$Parameter)

# plots

signal_color <- c('orange', 'brown', 'red', 'black', 'forestgreen', 'limegreen')

# ODT by SSC
plot_ly(DT, type = 'box', y = ~ODT, color = ~SSC, colors = signal_color, boxmean = TRUE)

# ODT vs gap
plot_ly(DT, type = 'scatter', x = ~ODT, y = ~Gap, color = ~SSC,
        mode = 'markers', colors = signal_color, symbol = ~Parameter, marker = list(size = 5))

# ODT vs TUG
plot_ly(DT[!(SSC %in% c('GG', 'GY')), ], type = 'scatter', x = ~ODT, y = ~TUG, color = ~SSC,
        mode = 'markers', colors = signal_color, marker = list(size = 5))

# ODT vs AIC
plot_ly(DT, type = 'scatter', x = ~ODT, y = ~AIC, color = ~SSC,
        mode = 'markers', colors = signal_color, marker = list(size = 5))

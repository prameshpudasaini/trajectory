library(data.table)
library(plotly)

DT <- fread("output/20221214_ISR_wb_3rd_19th.txt")
DT$EventID <- NULL

options(digits.secs = 3L)

DT[, TimeStamp := TimeStamp - 7 * 3600]
DT[, YellowStart := YellowStart - 7 * 3600]
DT[, RedStart := RedStart - 7 * 3600]
DT[, GreenStart := GreenStart - 7 * 3600]

SSC_levels <- c('YY', 'YR', 'RR', 'RG', 'GG', 'GY')
DT[, SSC := factor(as.factor(SSC), levels = SSC_levels)]

DT <- DT[Det != 'adv', ]

# plots
signal_color <- c('orange', 'brown', 'red', 'black', 'forestgreen', 'limegreen')

plot_ly(DT, type = 'box', y = ~ODT, color = ~SSC, colors = signal_color, boxmean = TRUE) |> 
    layout(yaxis = list(title = 'On-detector time (s)'),
           xaxis = list(title = 'Signal status change'))

plot_ly(DT, type = 'scatter', x = ~ODT, y = ~Gap, color = ~SSC,
                   mode = 'markers', colors = signal_color, marker = list(size = 5)) |> 
    layout(yaxis = list(title = 'Time gap (s)'),
           xaxis = list(title = 'On-detector time (s)'))

plot_ly(DT[!(SSC %in% c('GG', 'GY')), ], type = 'scatter', x = ~ODT, y = ~TUG, color = ~SSC,
                   mode = 'markers', colors = signal_color, marker = list(size = 5))

plot_ly(DT, type = 'scatter', x = ~ODT, y = ~AIC, color = ~SSC,
                   mode = 'markers', colors = signal_color, marker = list(size = 5)) |> 
    layout(yaxis = list(title = 'Arrival in cycle (s)'),
           xaxis = list(title = 'On-detector time (s)'))

# box plot of ODT ratio by intersection
plot_ly(DT, type = 'box', y = ~ODTR, color = ~Int, boxmean = TRUE)
plot_ly(DT, type = 'box', y = ~GapR, color = ~Int, boxmean = TRUE)

plot_ly(DT, type = 'scatter', x = ~ODT, y = ~ODTR, color = ~Int,
        mode = 'markers', marker = list(size = 5))

plot_ly(DT, type = 'scatter', x = ~TimeStamp, y = ~ODTR, color = ~Int, linetype = ~Parameter,
        mode = 'lines+markers', marker = list(size = 5))

plot_ly(DT, type = 'scatter', x = ~TimeStamp, y = ~ODT, color = ~Int, linetype = ~Parameter,
        mode = 'lines+markers', marker = list(size = 5))

plot_ly(DT, type = 'scatter', x = ~ODTR, y = ~AIC, color = ~Int,
        mode = 'markers', marker = list(size = 5))

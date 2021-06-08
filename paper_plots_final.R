install.and.load <- function(vPacotes)
{
  for (pac in vPacotes) {
    if (!require(pac, character.only=T)) {
      install.packages(pac)
      library(pac, character.only=T)
    }
  }
}

install.and.load(c('here', 'ggplot2', 'scales', 'grid', 'gridExtra', 
                   'dplyr', 'tidyr', 'stringr', 'plotly', 'ggthemes'))

if (!require("processx")) install.packages("processx")


dfRepTrialAppell_dm <- readRDS(file = "in/dfRepTrialAppell_dm.Rds")
dfAppellbyCID_dm <- readRDS(file = "in/dfAppellbyCID_dm.Rds")

dfRepTrialAppell_reemb <- readRDS(file = "in/dfRepTrialAppell_reemb.Rds")

dfRepTrial_req <- readRDS(file = "in/dfRepTrial_req.Rds")
dfAppellbyCID_reemb <- readRDS(file = "in/dfAppellbyCID_reemb.Rds")



GRAYS <- c('#cccccc', '#999999', '#666666', '#333333')

BLUES <- c('#AADDFF', '#77AACC', '#447799', '#114466')

LBLUE <- '#B3CDE3'

GREENS <- c("#00d19c", "#009e74", "#004f3b")
# GREENS <- c("#aaffc5", "#77cc98", "#116636")

doc.colors <- c(BLUES[1], BLUES[2], BLUES[4])
names(doc.colors) <- c("R", "1a", "2a")

proc.colors <- GRAYS
names(proc.colors) <- c("PROCEDIMENTO", "REEMBOLSO", "TRATAMENTO", "MEDICAMENTO_EME")

flag.colors <- c("#004f3b", "#cccccc")
names(flag.colors) <- c("Provided", "Not provided")

levels.colors <- c(GREENS[1], GREENS[2], GREENS[3])
names(levels.colors) <- c("lower", "equal", "higher")

m <- list(
  l = 50,
  r = 50,
  b = 100,
  t = 100,
  pad = 4
)

f <- list(
  size = 16
)

tit <- list(
  size = 12
)


af <- list(
  size = 12
)



# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#5.1 a

#remover os valores onde R é zero para melhorar a forma do boxplot
dfPlot <- dfRepTrialAppell_dm %>% filter(!(document == "R" & value == "0"))

xform <- list(categoryorder = "array",
              categoryarray = c("R", 
                                "1a", 
                                "2a"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
         title = "Granted values for moral damages: \nall law suits and appeals analyzed",
         yaxis = list(font = f, title = "Amount (R$)", dtick=50000), 
         xaxis = list(font = f, title = "", 
           ticktext = list("Report \n(N = 533)", "Lower Court \n(N = 3517)", "Appellate Court \n(N = 1243)"), 
           tickvals = list("R", "1a", "2a"),
           tickmode = "array",
           categoryarray = c("R","1a", "2a"),
           categoryorder = "array"),
          
         margin = m)

viz

orca(viz, "out/md_all_v3.pdf")

#5.1 b
dfPlot <- dfRepTrialAppell_dm %>% filter(!(document == "R" & value == "0"))
pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary[my_summary$type == "min",]$ypos <- my_summary[my_summary$type == "min",]$ypos + 1500
my_summary[my_summary$type != "min",]$value <- paste0(as.character(round((my_summary[my_summary$type != "min",]$value / 1000),1)), "k")

docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages: \nall law suits and appeals analyzed (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,110000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 533)", "Lower Court \n(N = 3517)", "Appellate Court \n(N = 1243)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_all_zoom_v3.pdf")

#5.1 c
dfPlot <- dfRepTrialAppell_dm %>% filter(!(document == "R" & value == "0"))

pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages: \nall law suits and appeals analyzed (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 533)", "Lower Court \n(N = 3517)", "Appellate Court \n(N = 1243)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_all_noout_v3.pdf")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#5.3 a

dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename))

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits: only denied appeals",
         yaxis = list(font=f, title = "Amount (R$)", dtick=50000), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 341)", "Lower Court\n(N = 2274)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_no_updecisions_v3.pdf")

#5.3 b
dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename))

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  options("scipen"=10)  
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary[my_summary$type == "min",]$ypos <- my_summary[my_summary$type == "min",]$ypos + 1500
my_summary[my_summary$type != "min",]$value <- paste0(as.character(round((my_summary[my_summary$type != "min",]$value / 1000),1)), "k")
# my_summary[my_summary$type == "min",]$value <- paste0(my_summary[my_summary$type == "min",]$value, "k")

docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages related to \nthe same law suits: only denied appeals (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,105000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 341)", "Lower Court\n(N = 2274)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_no_updecisions_zoom_v3.pdf")

# 5.3 c

dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename))

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits: only denied appeals (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 341)", "Lower Court\n(N = 2274)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE)  %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_no_updecisions_noout_v3.pdf")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#5.2 a

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename)

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits: only granted appeals",
         yaxis = list(font=f, title = "Amount (R$)", dtick=50000), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 192)", "Lower Court \n(N = 1243)", "Appellate Court \n(N = 1243)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_updecisions_v3.pdf")

#5.2 b

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename)

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary[my_summary$type == "min",]$ypos <- my_summary[my_summary$type == "min",]$ypos + 1500
my_summary[my_summary$type != "min",]$value <- paste0(as.character(round((my_summary[my_summary$type != "min",]$value / 1000),1)), "k")
# my_summary[my_summary$type == "min",]$value <- paste0(my_summary[my_summary$type == "min",]$value, "k")

docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages related to \nthe same law suits: only granted appeals (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,110000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 192)", "Lower Court \n(N = 1243)", "Appellate Court \n(N = 1243)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_updecisions_zoom_v3.pdf")

#5.2 c

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename)

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}


viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits: only granted appeals (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 192)", "Lower Court \n(N = 1243)", "Appellate Court \n(N = 1243)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_updecisions_noout_v3.pdf")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename & CID_NOME == "Ap. circulatório")

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(font=f, title = "",
         yaxis = list(title = "Amount (R$)", dtick=10000), 
         xaxis = list(title = "", 
                      ticktext = list("Report", "Lower Court", "Appellate Court"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_circ_updecisions.pdf")

pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}


viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(font=f, title = "",
         yaxis = list(title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(title = "", 
                      ticktext = list("Report", "Lower Court", "Appellate Court"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_circ_updecisions_noout.pdf")
  

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# 5.5 a

dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename) & CID_NOME == "Ap. circulatório")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout( title = "Granted values for moral damages related to \nthe same law suits of the Circulatory chapter:\nonly denied appeals",
         yaxis = list(font=f,title = "Amount (R$)", dtick=10000), 
         xaxis = list(font=f,title = "", 
                      ticktext = list("Report \n(N = 22)", "Lower Court\n(N = 134)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_circ_no_updecisions_v3.pdf")

#5.2 b


dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename) & CID_NOME == "Ap. circulatório")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500

my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")


docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages related to \nthe same law suits of the Circulatory chapter:\nonly denied appeals (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,105000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 22)", "Lower Court\n(N = 134)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_circ_no_updecisions_zomm_v3.pdf")

# 5.5 c

dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename) & CID_NOME == "Ap. circulatório")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))


pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}


viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits of the Circulatory chapter:\nonly denied appeals (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 22)", "Lower Court\n(N = 134)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_circ_no_updecisions_noout_v3.pdf")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# 5.4 a

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename & CID_NOME == "Ap. circulatório")


dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to\n the same law suits of the Circulatory chapter:\nonly granted appeals",
         yaxis = list(font=f, title = "Amount (R$)", dtick=10000), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 6)", "Lower Court\n(N = 64)", "Appellate Court\n(N = 64)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_circ_updecisions_v3.pdf")

#5.4 b

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename & CID_NOME == "Ap. circulatório")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
# my_summary$ypos <- my_summary[my_summary$type == "min",]$ypos + 1500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")
# my_summary[my_summary$type == "min",]$value <- paste0(my_summary[my_summary$type == "min",]$value, "k")

docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages related to\n the same law suits of the Circulatory chapter:\nonly granted appeals (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,105000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 6)", "Lower Court\n(N = 64)", "Appellate Court\n(N = 64)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_circ_updecisions_zomm_v3.pdf")

# 5.4 c

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename & CID_NOME == "Ap. circulatório")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}


viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to\n the same law suits of the Circulatory chapter:\nonly granted appeals (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 6)", "Lower Court\n(N = 64)", "Appellate Court\n(N = 64)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_circ_updecisions_noout_v3.pdf")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# 5.7 a

dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename) & CID_NOME == "Infecciosas")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits of the Infectious chapter: \nonly denied appeals",
         yaxis = list(font=f, title = "Amount (R$)", dtick=10000), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 38)", "Lower Court\n(N = 244)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_infec_no_updecisions_v3.pdf")

# 5.7 b

dfPlot <- dfRepTrialAppell_dm %>%
  filter(!(Filename %in% dfAppellbyCID_dm$Filename) & CID_NOME == "Infecciosas")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"), sep = ",")

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary[my_summary$type == "min",]$ypos <- my_summary[my_summary$type == "min",]$ypos + 1500
my_summary[my_summary$type != "min",]$value <- paste0(as.character(round((my_summary[my_summary$type != "min",]$value / 1000),1)), "k")


docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages related to \nthe same law suits of the Infectious chapter: \nonly denied appeals (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,105000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 38)", "Lower Court\n(N = 244)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_infec_no_updecisions_zomm_v3.pdf")

# 5.7 c

dfPlot <- dfRepTrialAppell_dm %>%
    filter(!(Filename %in% dfAppellbyCID_dm$Filename) & CID_NOME == "Infecciosas")
  
dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))
  
pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}



viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits of the Infectious chapter: \nonly denied appeals (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 38)", "Lower Court\n(N = 244)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_infec_no_updecisions_noout_v3.pdf")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

# 5.6 a

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename & CID_NOME == "Infecciosas")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits of the Infectious chapter: \nonly granted appeals",
         yaxis = list(font=f, title = "Amount (R$)", dtick=10000), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 21)", "Lower Court \n(N = 150)", "Appellate Court \n(N = 150)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m)

viz

orca(viz, "out/md_infec_updecisions_v3.pdf")

#5.6 b

dfPlot <- dfRepTrialAppell_dm %>%
  filter(Filename %in% dfAppellbyCID_dm$Filename & CID_NOME == "Infecciosas")

dfPlot <- dfPlot %>% filter(!(document == "R" & value == "0"))

pos <- c(0.5)
names(pos) <- c("R")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document == "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500

my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", colors = doc.colors, 
               showlegend = FALSE, width = 500, height = 500) %>%
  layout(
    title = "Granted values for moral damages related to \nthe same law suits of the Infectious chapter: \nonly granted appeals (zoom)",
    yaxis = list(font = f, title = "Amount (R$)",range = c(0,105000), dtick=10000), 
    xaxis = list(font = f, title = "", 
                 ticktext = list("Report \n(N = 21)", "Lower Court \n(N = 150)", "Appellate Court \n(N = 150)"), 
                 tickvals = list("R", "1a", "2a"),
                 tickmode = "array",
                 categoryarray = c("R","1a", "2a"),
                 categoryorder = "array"),
    
    margin = m)%>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_infec_updecisions_zoom_v3.pdf")

# 5.6 c
pos <- c(1.5, 2.5)
names(pos) <- c("1a", "2a")

docs <- unique(dfPlot$document)

my_summary <- data.frame(matrix(ncol=2,nrow=length(docs)))
colnames(my_summary) <- c("document", "stats")

for(i in 1:length(docs)){
  tempdf <- dfPlot %>% filter(document == docs[i])
  stats <- boxplot.stats(tempdf$value)$stats
  my_summary[i, "document"] <- docs[i]
  my_summary[i, "stats"] <- toString(stats)
}

my_summary <-  my_summary %>%
  separate(stats, c("min", "q1", "med", "q3", "uw"))

my_summary <- my_summary %>% filter(document != "R")

my_summary <- my_summary %>% gather(key = type, value = value, -c(document)) %>% as.data.frame()

my_summary$value <- as.numeric(my_summary$value)

my_summary$document <- pos[my_summary$document]
my_summary$ypos <- my_summary$value + 500
my_summary$value <- paste0(as.character(round((my_summary$value / 1000),1)), "k")

docs <- unique(my_summary$document)

for(i in 1:length(docs)){
  tempdf <- my_summary %>% filter(document == docs[i])
  if(tempdf[tempdf$type == "min", "value"] == tempdf[tempdf$type == "q1", "value"] ){
    old_value <- my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"]
    my_summary[(my_summary$type == "q1" & my_summary$document == docs[i]), "ypos"] <-  old_value + 1000
  }
}

viz <- plot_ly(dfPlot, y = ~value, color = ~document, type = "box", 
               colors = doc.colors,  showlegend = FALSE, 
               width = 500, height = 500) %>%
  layout(title = "Granted values for moral damages related to \nthe same law suits of the Infectious chapter: \nonly granted appeals (zoom)",
         yaxis = list(font=f, title = "Amount (R$)", range = c(0,26000), dtick=2500), 
         xaxis = list(font=f, title = "", 
                      ticktext = list("Report \n(N = 21)", "Lower Court \n(N = 150)", "Appellate Court \n(N = 150)"), 
                      tickvals = list("R", "1a", "2a"),
                      tickmode = "array",
                      categoryarray = c("R","1a", "2a"),
                      categoryorder = "array"),
         margin = m) %>% 
  add_annotations(font=af,
                  x = my_summary$document,
                  y = my_summary$ypos,
                  text = paste0(my_summary$type, ": ", my_summary$value),
                  textposition='top left', 
                  showarrow = FALSE) 

viz

orca(viz, "out/md_infec_updecisions_noout_v3.pdf")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

cids_names <- c("Undefined", "Infectious", "Neoplasm", "Blood", "Endocrine", "Mental", "Nervous", "Eye", "Ear", 
                       "Circulatory", "Respiratory", "Digestive", "Skin", "Musculoskeletal", "Genitourinary", "Childbirth and post-childbirth", 
                       "Perinatal", "Congenital", "Exams", "Poisoning", "Death", "Health services", "Not informed")

names(cids_names) <- c("Indefinido", "Infecciosas", "Tumores", "Sangue", "Endócrinas", "Mentais", "Sistema nervoso", "Oftalmológicas", "Auditivas",
                       "Ap. circulatório", "Ap. respiratório", "Ap. Digestivo",  "Dermatológicas", "Osteomuscular", "Ap. Urinário", "Parto e pós-parto",
                       "Gravidez", "Congênitas", "Exames", "Envenenamento", "Morte", "Serviço saúde", "Não informado")


dfRepTrialAppell_reemb[, "CID_NOME_EN"] <- cids_names[dfRepTrialAppell_reemb$CID_NOME]

#só casos que tiveram primeira instância
temp <- dfRepTrialAppell_reemb %>% 
  filter((!(Filename %in% dfAppellbyCID_reemb$Filename)))

#só casos que tiveram reembolso
documents_id <- temp %>% 
  filter(document == "1a") %>% filter(REEMBOLSO == "1") %>% select(Filename)

temp <- dfRepTrialAppell_reemb
temp[temp$document == "1a", "document"] <- "primeira"
temp[temp$document == "2a", "document"] <- "segunda"

temp <- temp %>% 
  filter(Filename %in% documents_id$Filename) %>%
  select(Filename, document, RVALOR, CID_NOME, CID_NOME_EN) %>% 
  group_by(Filename, CID_NOME) %>% 
  spread(document, RVALOR) %>%
  mutate(diff_Trial = primeira - R) %>% as.data.frame()

temp$diff_Trial_quali <- "equal"
temp[temp$diff_Trial > 0, "diff_Trial_quali"] <- "higher"
temp[temp$diff_Trial < 0, "diff_Trial_quali"] <- "lower"

temp$CID_NOME_EN <- as.factor(temp$CID_NOME_EN)
temp$diff_Trial_quali <- as.factor(temp$diff_Trial_quali)

temp2 <- temp %>% group_by(CID_NOME_EN, diff_Trial_quali) %>% 
  summarise(n=length(diff_Trial)) 

yform <- list(categoryorder = "array",
              categoryarray = temp2$n)

temp3 <- temp2 %>% filter(CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined") %>% group_by(CID_NOME_EN) %>% summarise(sum = sum(n))

n_order <- temp3[order(-temp3$sum),]

dfPlot <- temp2 %>% filter(CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined")

dfPlot$CID_NOME_EN <- factor(dfPlot$CID_NOME_EN, levels = n_order$CID_NOME_EN) 
dfPlot$diff_Trial_quali <- factor(dfPlot$diff_Trial_quali, levels = c("lower", "equal", "higher")) 

viz <-  plot_ly(dfPlot, y= ~CID_NOME_EN , x = ~n, color=~diff_Trial_quali, colors = levels.colors, 
                type = "bar", showlegend = TRUE, width = 1000, height = 500) %>%
  layout(yaxis = list(font=f,title ='', yform),
         xaxis = list(font=f,title=''),
         barmode = 'group',
         title = 'Material damages granted by chapter:\nonly denied appeals',
         autosize = FALSE) 

viz


orca(viz, "out/md_reemb_no_updecisions_v3.pdf")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#só casos que tiveram 2a instância
temp <- dfRepTrialAppell_reemb %>% 
  filter(Filename %in% dfAppellbyCID_reemb$Filename)

#só casos que tiveram reembolso
documents_id <- temp %>% 
  filter(document == "2a") %>% filter(REEMBOLSO == "1") %>% select(Filename)

temp <- dfRepTrialAppell_reemb
temp[temp$document == "1a", "document"] <- "primeira"
temp[temp$document == "2a", "document"] <- "segunda"

temp <- temp %>% 
  filter(Filename %in% documents_id$Filename) %>%
  select(Filename, document, RVALOR, CID_NOME, CID_NOME_EN) %>% 
  group_by(Filename, CID_NOME) %>% 
  spread(document, RVALOR) %>%
  mutate(diff_Appell = segunda - R) %>% as.data.frame()

temp$diff_Appell_quali <- "equal"
temp[temp$diff_Appell > 0, "diff_Appell_quali"] <- "higher"
temp[temp$diff_Appell < 0, "diff_Appell_quali"] <- "lower"

temp$CID_NOME_EN <- as.factor(temp$CID_NOME_EN)
temp$diff_Appell_quali <- as.factor(temp$diff_Appell_quali)


temp2 <- temp %>% group_by(diff_Appell_quali) %>% 
  summarise(n=length(diff_Appell)) 
# complete(CID_NOME, nesting(diff_Appell_quali), fill = list(n = 0))

yform <- list(categoryorder = "array",
              categoryarray = temp2$n)

dfPlot <- temp2 

dfPlot$diff_Appell_quali <- factor(dfPlot$diff_Appell_quali, levels = c("lower", "equal", "higher")) 

viz <-  plot_ly(dfPlot, y= ~diff_Appell_quali , x = ~n, color=~diff_Appell_quali, 
                colors = levels.colors, 
                type = "bar", showlegend = TRUE) %>%
  layout(font=f, yaxis = list(title ='', yform),
         xaxis = list(title='', dtick=2),
         barmode = 'group',
         title = '') 

viz

orca(viz, "out/md_reemb_no_updecisions.pdf")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

documents_req <- dfRepTrialAppell_reemb %>% filter(REEMBOLSO == 1 & document == "2a") %>% select("Filename")

#só casos que tiveram primeira instância
temp <- dfRepTrialAppell_reemb %>% 
  filter((!(Filename %in% dfAppellbyCID_reemb$Filename)))
documents_req2 <- dfRepTrialAppell_reemb %>% filter(Filename %in% temp$Filename & REEMBOLSO == 1) %>% select("Filename")

documents_all <- rbind(documents_req, documents_req2)

cids_names <- c("Undefined", "Infectious", "Neoplasm", "Blood", "Endocrine", "Mental", "Nervous", "Eye", "Ear", 
                "Circulatory", "Respiratory", "Digestive", "Skin", "Musculoskeletal", "Genitourinary", "Childbirth and post-childbirth", 
                "Perinatal", "Congenital", "Exams", "Poisoning", "Death", "Health services", "Not informed")

names(cids_names) <- c("Indefinido", "Infecciosas", "Tumores", "Sangue", "Endócrinas", "Mentais", "Sistema nervoso", "Oftalmológicas", "Auditivas",
                       "Ap. circulatório", "Ap. respiratório", "Ap. Digestivo",  "Dermatológicas", "Osteomuscular", "Ap. Urinário", "Parto e pós-parto",
                       "Gravidez", "Congênitas", "Exames", "Envenenamento", "Morte", "Serviço saúde", "Não informado")

dfRepTrialAppell_reemb[, "CID_NOME_EN"] <- cids_names[dfRepTrialAppell_reemb$CID_NOME]

dfReemb <- dfRepTrialAppell_reemb %>%
  group_by(CID_NOME, document, CID_NOME_EN) %>%
  filter(REEMBOLSO == "1" & Filename %in% documents_all$Filename & CID_NOME_EN != "Undefined" & CID_NOME_EN != "Not informed") %>%
  tally()

temp <- dfReemb %>% spread(document, n)
temp[is.na(temp$`1a`), "1a"] <- 0
temp[is.na(temp$`2a`), "2a"] <- 0

colnames(temp) <- c("CID_NOME", "CID_NOME_EN", "primeira", "segunda", "R")

dfPlot <- temp %>% group_by(CID_NOME, CID_NOME_EN) %>% mutate(Provided = primeira + segunda,
                                                              Not_provided = R - segunda - primeira)

dfPlot <- dfPlot %>% select(-c(R, primeira, segunda)) %>% gather(key = type, value = value, -c(CID_NOME, CID_NOME_EN))

dfPlot[dfPlot$type == "Not_provided", "type"] <- "Not provided"

temp <- dfPlot %>%
  group_by(CID_NOME_EN) %>% summarise(sum = sum(value))

n_order <- temp[order(-temp$sum),]

dfPlot$CID_NOME_EN <- factor(dfPlot$CID_NOME_EN, levels = n_order$CID_NOME_EN)

dfPlot$type <- factor(dfPlot$type, levels = c("Provided", "Not provided")) 

viz <-  plot_ly(dfPlot, y= ~CID_NOME_EN , x = ~value, color=~type, colors = flag.colors,
                type = "bar", showlegend = TRUE, width = 1000, height = 500) %>%
  layout(barmode = 'stack',
         title = 'Relation between material damage claims \nand decisions of such claims by chapter',
         xaxis = list(font=f, title ='', dtick=10),
         yaxis = list(font=f, title ='')) 

viz

orca(viz, "out/reemb_all_v3.pdf")


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

documents_req <- dfRepTrial_req %>% filter(type == "PROCEDIMENTO" & document == "R" & value == "1") %>% select("Filename")

cids_names <- c("Undefined", "Infectious", "Neoplasm", "Blood", "Endocrine", "Mental", "Nervous", "Eye", "Ear", 
                "Circulatory", "Respiratory", "Digestive", "Skin", "Musculoskeletal", "Genitourinary", "Childbirth and post-childbirth", 
                "Perinatal", "Congenital", "Exams", "Poisoning", "Death", "Health services", "Not informed")

names(cids_names) <- c("Indefinido", "Infecciosas", "Tumores", "Sangue", "Endócrinas", "Mentais", "Sistema nervoso", "Oftalmológicas", "Auditivas",
                       "Ap. circulatório", "Ap. respiratório", "Ap. Digestivo",  "Dermatológicas", "Osteomuscular", "Ap. Urinário", "Parto e pós-parto",
                       "Gravidez", "Congênitas", "Exames", "Envenenamento", "Morte", "Serviço saúde", "Não informado")

dfRepTrial_req[, "CID_NOME_EN"] <- cids_names[dfRepTrial_req$CID_NOME]

temp <- dfRepTrial_req %>%
  group_by(CID_NOME, document, type, value, CID_NOME_EN) %>%
  filter(type == "PROCEDIMENTO" & Filename %in% documents_req$Filename & CID_NOME_EN != "Undefined") %>%
  tally()


temp <- temp %>% filter(document != "R")

temp2 <- temp %>%
  group_by(CID_NOME_EN) %>% summarise(sum = sum(n))

n_order <- temp2[order(-temp2$sum),]

dfPlot <- temp %>% filter(CID_NOME_EN != "Undefined" & CID_NOME_EN != "Not informed")

dfPlot$CID_NOME_EN <- factor(dfPlot$CID_NOME_EN, levels = n_order$CID_NOME_EN)


values_name <- c("Provided", "Not provided")
names(values_name) <- c("1", "0")

dfPlot[, "names_EN"] <- values_name[dfPlot$value]
dfPlot$names_EN <- factor(dfPlot$names_EN, levels = c("Provided", "Not provided")) 

viz <-  plot_ly(dfPlot, y= ~CID_NOME_EN , x = ~n, color=~names_EN, colors = flag.colors,
                type = "bar", showlegend = TRUE, width = 1000, height = 500) %>%
  layout(barmode = 'stack',
         title = 'Relation between procedure claims and \nlower Court decisions of such claims by chapter',
         xaxis = list(font=f, title ='', dtick=10),
         yaxis = list(font=f, title ='')) 

viz

orca(viz, "out/proced_no_updecisions_v3.pdf")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

documents_req <- dfRepTrial_req %>% filter(type == "MEDICAMENTO_EME" & document == "R" & value == "1") %>% select("Filename")

temp <- dfRepTrial_req %>%
  group_by(CID_NOME, document, type, value, CID_NOME_EN) %>%
  filter(type == "MEDICAMENTO_EME" & Filename %in% documents_req$Filename & CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined") %>%
  tally()

temp <- temp %>% filter(document != "R")

temp2 <- temp %>% filter(CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined") %>%
  group_by(CID_NOME_EN) %>% summarise(sum = sum(n))

n_order <- temp2[order(-temp2$sum),]

dfPlot <- temp %>% filter(CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined")

dfPlot$CID_NOME_EN <- factor(dfPlot$CID_NOME_EN, levels = n_order$CID_NOME_EN) 


values_name <- c("Provided", "Not provided")
names(values_name) <- c("1", "0")

dfPlot[, "names_EN"] <- values_name[dfPlot$value]
dfPlot$names_EN <- factor(dfPlot$names_EN, levels = c("Provided", "Not provided")) 

viz <-  plot_ly(dfPlot, y= ~CID_NOME_EN , x = ~n, color=~names_EN, colors = flag.colors,
                type = "bar", showlegend = TRUE, width = 1000, height = 500) %>%
  layout(barmode = 'stack',
         title = 'Relation between medicine/exam claims and \nlower Court decisions of such claims by chapter',
         xaxis = list(font=f, title ='', dtick=10),
         yaxis = list(font=f, title ='')) 

viz

orca(viz, "out/medic_no_updecisions_v3.pdf")

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

documents_req <- dfRepTrial_req %>% filter(type == "TRATAMENTO" & document == "R" & value == "1") %>% select("Filename")

temp <- dfRepTrial_req %>%
  group_by(CID_NOME, document, type, value, CID_NOME_EN) %>%
  filter(type == "TRATAMENTO" & Filename %in% documents_req$Filename & CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined") %>%
  tally()

temp <- temp %>% filter(document != "R")

temp2 <- temp %>% filter(CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined") %>%
  group_by(CID_NOME_EN) %>% summarise(sum = sum(n))

n_order <- temp2[order(-temp2$sum),]

dfPlot <- temp %>% filter(CID_NOME_EN != "Not informed" & CID_NOME_EN != "Undefined")

dfPlot$CID_NOME_EN <- factor(dfPlot$CID_NOME_EN, levels = n_order$CID_NOME_EN) 


values_name <- c("Provided", "Not provided")
names(values_name) <- c("1", "0")

dfPlot[, "names_EN"] <- values_name[dfPlot$value]
dfPlot$names_EN <- factor(dfPlot$names_EN, levels = c("Provided", "Not provided")) 

viz <-  plot_ly(dfPlot, y= ~CID_NOME_EN , x = ~n, color=~names_EN, colors = flag.colors,
                type = "bar", showlegend = TRUE, width = 1000, height = 500) %>%
  layout(barmode = 'stack',
         title = 'Relation between treatment claims and \nlower Court decisions of such claims by chapter',
         xaxis = list(font=f, title ='', dtick=10),
         yaxis = list(font=f, title ='')) 

viz

orca(viz, "out/trat_no_updecisions_v3.pdf")


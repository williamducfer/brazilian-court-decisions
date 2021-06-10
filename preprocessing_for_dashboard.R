# Report =======================================================================================

dfRep_orig <-
  read.csv(
    file = here(
      'in',
      'report_preprocessed.csv'
    ),
    sep = ';',
    stringsAsFactors = F,
    na.strings = "NA"
  )

names(dfRep_orig) = gsub(pattern = "X.",
                         replacement = "",
                         x = names(dfRep_orig))

saveRDS(dfRep_orig, file = "in/dfRep_orig.Rds")
dfRep <- dfRep_orig

head(dfRep)
names(dfRep)
summary(dfRep)
length(unique(dfRep$Filename))

# REEMBOLSO - Material damage #

# fixing some inconsistencies - written out numbers in VALOR_REEMBOLSO column
temp <- dfRep
temp[temp$Filename == "0473720-05.2015.8.19.0001.txt", "VALOR_REEMBOLSO_PREPROCESSED"] = "6000.0"

temp$VALOR_REEMBOLSO_PREPROCESSED_temp <-
  temp$VALOR_REEMBOLSO_PREPROCESSED

# adding up the refund amounts that are separate
temp <-
  temp %>% separate(
    VALOR_REEMBOLSO_PREPROCESSED_temp,
    c(
      "VALOR_REEMBOLSO_PREPROCESSED_1",
      "VALOR_REEMBOLSO_PREPROCESSED_2"
    ),
    "\n"
  )

# transforming 0 > NA
temp[is.na(temp)] = 0
temp[temp == ""] = 0

temp$VALOR_REEMBOLSO_PREPROCESSED_total <-
  as.numeric(temp$VALOR_REEMBOLSO_PREPROCESSED_1) + as.numeric(temp$VALOR_REEMBOLSO_PREPROCESSED_2)

# removing the temporary columns I created to add up (previous step)
temp$VALOR_REEMBOLSO_PREPROCESSED_1 <- NULL
temp$VALOR_REEMBOLSO_PREPROCESSED_2 <- NULL

# DANO MORAL - moral damage #

# fixing some inconsistencies - written out numbers in VALOR_DANO_MORAL column

short_val <-
  c(
    "20000.0",
    "20000.0",
    "30000.0",
    "60000.0",
    "60000.0",
    "61000.0",
    "100000.0",
    "400000.0",
    "40000.0",
    "200000.0",
    "10000.0",
    "50000.0",
    "70000.0"
  )

long_val <-
  c(
    "vinte salários mínimos",
    "vinte mil reais",
    "trinta mil reais",
    "sessenta salários mínimos",
    "sessenta Salários - Mínimos",
    "sessenta e um salários mínimos",
    "cem salários mínimos",
    "quatrocentos salários mínimos",
    "quarenta salários mínimos",
    "duzentos salários mínimos",
    "dez mil reais",
    "cinquenta salários mínimos",
    "setenta salários mínimos"
  )

names(short_val) <- long_val

temp$VALOR_DANO_MORAL_PREPROCESSED_temp <-
  temp$VALOR_DANO_MORAL_PREPROCESSED
pos <-
  which(str_detect(temp$VALOR_DANO_MORAL, "[[:digit:]]|r$") == FALSE)

temp$VALOR_DANO_MORAL_PREPROCESSED_temp[pos] <-
  str_replace_all(temp$VALOR_DANO_MORAL[pos], short_val)

temp[temp$VALOR_DANO_MORAL == "20 sm", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "20000.0"
temp[temp$VALOR_DANO_MORAL == "50\nsalários mínimos", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "50000.0"
temp[temp$VALOR_DANO_MORAL == "45\nsalários mínimos", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "45000.0"
temp[temp$VALOR_DANO_MORAL == "r$ 30 mil .", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "30000.0"
temp[temp$VALOR_DANO_MORAL == "60 ( sessenta\nsalários mínimos", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "60000.0"
temp[temp$VALOR_DANO_MORAL == "30 trinta ) salários mínimos", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "30000.0"
temp[temp$VALOR_DANO_MORAL_temp == "20.0 0.0", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "20000.0"

temp <-
  temp %>% separate(
    VALOR_DANO_MORAL_PREPROCESSED_temp,
    c(
      "VALOR_DANO_MORAL_PREPROCESSED_1",
      "VALOR_DANO_MORAL_PREPROCESSED_2"
    ),
    "\n"
  )
temp[is.na(temp)] = 0
temp[temp == ""] = 0

temp$VALOR_DANO_MORAL_PREPROCESSED_total <-
  as.numeric(temp$VALOR_DANO_MORAL_PREPROCESSED_1) + as.numeric(temp$VALOR_DANO_MORAL_PREPROCESSED_2)

temp$VALOR_DANO_MORAL_PREPROCESSED_1 <- NULL
temp$VALOR_DANO_MORAL_PREPROCESSED_2 <- NULL


dfRep <- temp

# transforming some columns into flags
dfRep[dfRep$PEDIU_MEDICAMENTO_EME != "0", "PEDIU_MEDICAMENTO_EME"] <-
  1

dfRep[dfRep$PEDIU_PROCEDIMENTO != "0", "PEDIU_PROCEDIMENTO"] <- 1

dfRep[dfRep$PEDIU_REEMBOLSO != "0", "PEDIU_REEMBOLSO"] <- 1

dfRep[dfRep$PEDIU_TRATAMENTO != "0", "PEDIU_TRATAMENTO"] <- 1

# if it has value in VALOR_REEMBOLSO_PREPROCESSED, PEDIU_REEMBOLSO must be 1
dfRep[dfRep$VALOR_REEMBOLSO_PREPROCESSED_total != "0", "PEDIU_REEMBOLSO"] <-
  1


# separating CID
dfRep$CID_GRUPO <-
  gsub("\\s+", ",", gsub("^\\s+|\\s+$", "", dfRep$CID_GRUPO))

dfRep <-  dfRep %>%
  rowwise() %>%
  mutate(CID_GRUPO = paste(unique(str_sort(unlist(
    strsplit(CID_GRUPO, ",", fixed = TRUE)
  ))),
  collapse = ","))

dfRep$CID_GRUPO <- sort(dfRep$CID_GRUPO)

saveRDS(dfRep, file = "in/dfRep.Rds")


# checking if there is values in pediu_reembolso == 1
temp <-
  dfRep %>% filter(PEDIU_REEMBOLSO == "1" &
                     VALOR_REEMBOLSO_PREPROCESSED_total == "0")
# 262 casos onde isto acontece, devemos pegar o valor da 1a instância

id_Rep_error <- temp$Filename


# Trial ========================================================================================

dfTrial_orig <-
  read.csv(
    file = here(
      'in',
      'lower_preprocessed.csv'
    ),
    sep = ';',
    stringsAsFactors = F,
    na.strings = "NA"
  )

names(dfTrial_orig) = gsub(pattern = "X.",
                           replacement = "",
                           x = names(dfTrial_orig))

saveRDS(dfTrial_orig, file = "in/dfTrial_orig.Rds")

dfTrial <- dfTrial_orig

head(dfTrial)
names(dfTrial)
length(unique(dfTrial$Filename))

# some values in VALOR_REEMBOLSO_PREPROCESSED were in the wrong column
pos <-
  which(dfTrial$REEMBOLSO != "0" &
          grepl("\\d+(?:,\\d+)?", dfTrial$REEMBOLSO))

dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  dfTrial[pos, "REEMBOLSO"]
dfTrial[pos, "REEMBOLSO"] <- "1"

dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  str_extract(dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"], '[0-9]+\\.[0-9]+\\,[0-9]+|[0-9]+\\,[0-9]+')
dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  str_replace(dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"], "\\.", "")
dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  str_replace(dfTrial[pos, "VALOR_REEMBOLSO_PREPROCESSED"], "\\,", ".")


# REEMBOLSO - Material damage #

# fixing some inconsistencies - written out numbers in VALOR_REEMBOLSO column
temp <- dfTrial

temp[temp$Filename == "0473720-05.2015.8.19.0001.txt", "VALOR_REEMBOLSO_PREPROCESSED"] = "6000.0"

temp$VALOR_REEMBOLSO_PREPROCESSED_temp <-
  temp$VALOR_REEMBOLSO_PREPROCESSED

temp <-
  temp %>% separate(
    VALOR_REEMBOLSO_PREPROCESSED_temp,
    c(
      "VALOR_REEMBOLSO_PREPROCESSED_1",
      "VALOR_REEMBOLSO_PREPROCESSED_2"
    ),
    "\n"
  )
temp[is.na(temp)] = 0
temp[temp == ""] = 0

temp$VALOR_REEMBOLSO_PREPROCESSED_total <-
  as.numeric(temp$VALOR_REEMBOLSO_PREPROCESSED_1) + as.numeric(temp$VALOR_REEMBOLSO_PREPROCESSED_2)

temp$VALOR_REEMBOLSO_PREPROCESSED_1 <- NULL
temp$VALOR_REEMBOLSO_PREPROCESSED_2 <- NULL

# DANO MORAL - moral damage#

# fixing some inconsistencies - written out numbers in VALOR_DANO_MORAL column
short_val <-
  c(
    "20000.0",
    "7000.0",
    "6000.0",
    "8000.0",
    "40000.0",
    "10000.0",
    "5000.0",
    "50000.0",
    "4000.0"
  )

long_val <-
  c(
    "vinte mil reais",
    "sete mil reais",
    "seis mil reais",
    "oito mil reais",
    "quarenta mil reais",
    "dez mil reais",
    "cinco mil reais",
    "cinquenta mil reais",
    "quatro mil reais"
  )

names(short_val) <- long_val

temp$VALOR_DANO_MORAL_PREPROCESSED_temp <-
  temp$VALOR_DANO_MORAL_PREPROCESSED
pos <-
  which(str_detect(temp$VALOR_DANO_MORAL, "[[:digit:]]") == FALSE)

temp$VALOR_DANO_MORAL_PREPROCESSED_temp[pos] <-
  str_replace_all(temp$VALOR_DANO_MORAL[pos] , short_val)

temp[temp$VALOR_DANO_MORAL == "vinte mil reais ( r$ 20.000,00 )", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "20000.0"
temp[temp$VALOR_DANO_MORAL == "der$2.000,00 ( dois mil reais )", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "2000.0"
temp[temp$VALOR_DANO_MORAL == "pagar r$ 4.000,00 ( quatro mil reais )", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "4000.0"
temp[temp$VALOR_DANO_MORAL == "R4 2.500,00", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "2500.0"
temp[temp$VALOR_DANO_MORAL == "$ 10.000,00 ( dez mil reais )", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "10000.0"
temp[temp$VALOR_DANO_MORAL == "reais )\noito mil reais", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "8000.0"
temp[temp$VALOR_DANO_MORAL == "r$ $ 10.000,00 ( dez mil reais )", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "10000.0"
temp[temp$VALOR_DANO_MORAL == "r%5.000,00 ( cinco mil Reais )", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "5000.0"
temp[temp$VALOR_DANO_MORAL == "dez mil reais ,", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = "10000.0"
temp[temp$VALOR_DANO_MORAL == "mesmo valor", "VALOR_DANO_MORAL_PREPROCESSED_temp"] = ""

temp <-
  temp %>% separate(
    VALOR_DANO_MORAL_PREPROCESSED_temp,
    c(
      "VALOR_DANO_MORAL_PREPROCESSED_1",
      "VALOR_DANO_MORAL_PREPROCESSED_2"
    ),
    "\n"
  )
temp[is.na(temp)] = 0
temp[temp == ""] = 0

temp$VALOR_DANO_MORAL_PREPROCESSED_total <-
  as.numeric(temp$VALOR_DANO_MORAL_PREPROCESSED_1) + as.numeric(temp$VALOR_DANO_MORAL_PREPROCESSED_2)

temp$VALOR_DANO_MORAL_PREPROCESSED_1 <- NULL
temp$VALOR_DANO_MORAL_PREPROCESSED_2 <- NULL

dfTrial <- temp

# transforming some columns into flags

dfTrial[dfTrial$MEDICAMENTO_EME != "0", "MEDICAMENTO_EME"] <- 1

dfTrial[dfTrial$PROCEDIMENTO != "0", "PROCEDIMENTO"] <- 1

dfTrial[dfTrial$REEMBOLSO != "0", "REEMBOLSO"] <- 1

dfTrial[dfTrial$TRATAMENTO != "0", "TRATAMENTO"] <- 1


# If VALOR_REEMBOLSO_PREPROCESSED != 0, REEMBOLSO must be 1
dfTrial[dfTrial$VALOR_REEMBOLSO_PREPROCESSED != "0", "REEMBOLSO"] <-
  1

saveRDS(dfTrial, file = "in/dfTrial.Rds")

# get the zeroed refund amounts in the order
temp <-
  dfTrial %>% filter(Filename %in% id_Rep_error) %>% select("Filename", "VALOR_REEMBOLSO_PREPROCESSED_total")

dfRep$VALOR_REEMBOLSO_PREPROCESSED_total[dfRep$Filename %in% temp$Filename] <-
  temp$VALOR_REEMBOLSO_PREPROCESSED_total[temp$Filename %in% dfRep$Filename]

saveRDS(dfRep, file = "in/dfRep.Rds")


# Appell =======================================================================================

dfAppell_orig <-
  read.csv(
    file = here(
      'in',
      'appellate_preprocessed.csv'
    ),
    sep = ';',
    stringsAsFactors = F,
    na.strings = "NA"
  )

names(dfAppell_orig) = gsub(
  pattern = "X.",
  replacement = "",
  x = names(dfAppell_orig)
)
colnames(dfAppell_orig)[2] <- "EXCLUIU"

saveRDS(dfAppell_orig, file = "in/dfAppell_orig.Rds")

dfAppell <- dfAppell_orig

head(dfAppell)
names(dfAppell)
summary(dfAppell)
length(unique(dfAppell$Filename))

# some VALOR_REEMBOLSO_PREPROCESSED values were in the wrong column
pos <-
  which(dfAppell$REEMBOLSO != "0" &
          grepl("\\d+(?:,\\d+)?", dfAppell$REEMBOLSO))

dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  dfAppell[pos, "REEMBOLSO"]
dfAppell[pos, "REEMBOLSO"] <- "1"

dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  str_extract(dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"], '[0-9]+\\.[0-9]+\\,[0-9]+|[0-9]+\\,[0-9]+')
dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  str_replace(dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"], "\\.", "")
dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"] <-
  str_replace(dfAppell[pos, "VALOR_REEMBOLSO_PREPROCESSED"], "\\,", ".")

# ajustando alguns textos para flags
dfAppell[dfAppell$EXCLUIU == "", "EXCLUIU"] <- 0
dfAppell[dfAppell$EXCLUIU != 0, "EXCLUIU"] <- 1
dfAppell[dfAppell$REEMBOLSO == "", "REEMBOLSO"] <- 0
dfAppell[dfAppell$REEMBOLSO != 0, "REEMBOLSO"] <- 1

# REEMBOLSO - Material damage #

# fixing some inconsistencies - written out numbers in VALOR_REEMBOLSO column
temp <- dfAppell

temp[temp$VALOR_REEMBOLSO == "50 % de as custas", "VALOR_REEMBOLSO_PREPROCESSED"] = ""

temp$VALOR_REEMBOLSO_PREPROCESSED_temp <-
  temp$VALOR_REEMBOLSO_PREPROCESSED

temp <-
  temp %>% separate(
    VALOR_REEMBOLSO_PREPROCESSED_temp,
    c(
      "VALOR_REEMBOLSO_PREPROCESSED_1",
      "VALOR_REEMBOLSO_PREPROCESSED_2"
    ),
    "\n"
  )
temp[is.na(temp)] = 0
temp[temp == ""] = 0

temp$VALOR_REEMBOLSO_PREPROCESSED_total <-
  as.numeric(temp$VALOR_REEMBOLSO_PREPROCESSED_1) + as.numeric(temp$VALOR_REEMBOLSO_PREPROCESSED_2)

temp$VALOR_REEMBOLSO_PREPROCESSED_1 <- NULL
temp$VALOR_REEMBOLSO_PREPROCESSED_2 <- NULL

# DANO MORAL - Moral damage#

# fixing some inconsistencies - written out numbers in VALOR_DANO_MORAL column
temp[temp$VALOR_DANO_MORAL == "afastar", "VALOR_DANO_MORAL_PREPROCESSED"] = ""
temp[temp$VALOR_DANO_MORAL == "10 % ( dez por cento ) sobre o valor de a condenação ,", "VALOR_DANO_MORAL_PREPROCESSED"] = ""
temp[temp$VALOR_DANO_MORAL == "de r$ 10.000,00 ( dez mil reais )", "VALOR_DANO_MORAL_PREPROCESSED"] = "10000.0"
temp[temp$VALOR_DANO_MORAL == "dez mil reais", "VALOR_DANO_MORAL_PREPROCESSED"] = "10000.0"

temp$VALOR_DANO_MORAL_PREPROCESSED_temp <-
  temp$VALOR_DANO_MORAL_PREPROCESSED
temp <-
  temp %>% separate(
    VALOR_DANO_MORAL_PREPROCESSED_temp,
    c(
      "VALOR_DANO_MORAL_PREPROCESSED_1",
      "VALOR_DANO_MORAL_PREPROCESSED_2"
    ),
    "\n"
  )
temp[is.na(temp)] = 0
temp[temp == ""] = 0

temp$VALOR_DANO_MORAL_PREPROCESSED_total <-
  as.numeric(temp$VALOR_DANO_MORAL_PREPROCESSED_1) + as.numeric(temp$VALOR_DANO_MORAL_PREPROCESSED_2)

temp$VALOR_DANO_MORAL_PREPROCESSED_1 <- NULL
temp$VALOR_DANO_MORAL_PREPROCESSED_2 <- NULL

dfAppell <- temp

# some entries do not appear in the report but appear in the lower court

# > length(unique(dfRep$Filename))
# [1] 3180
# > length(unique(dfTrial$Filename))
# [1] 3317
# > length(unique(dfAppell$Filename))
# [1] 1250

# > length(dfAppell$Filename %in% dfTrial$Filename)
# [1] 1250
# todos da 2a estão na 1a

# > length(dfAppell$Filename %in% dfRep$Filename)
# [1] 1250
# todos da 2a estão no relatório

documents_trial <- dfTrial$Filename

dfRep <- dfRep %>% filter(Filename %in% documents_trial)
documents_rep <- dfRep$Filename

dfTrial <- dfTrial %>% filter(Filename %in% documents_rep)

dfAppell <- dfAppell %>% filter(Filename %in% documents_rep)

# > length(unique(dfRep$Filename))
# [1] 3179
#   > length(unique(dfTrial$Filename))
# [1] 3179
#   > length(unique(dfAppell$Filename))
# [1] 1113

# if reembolso == 1 in Trial, PEDIU_REEMBOLSO must be 1 em Report
temp <- dfTrial %>% filter(REEMBOLSO == "1")
t_documents <- temp$Filename
dfRep[dfRep$Filename %in% t_documents, "PEDIU_REEMBOLSO"] <- 1

temp <- dfAppell %>% filter(REEMBOLSO == "1")
t_documents <- temp$Filename
dfRep[dfRep$Filename %in% t_documents, "PEDIU_REEMBOLSO"] <- 1


# if EXCLUIU == 0 AND VALOR == 0, get the value in Lower court
temp <-
  dfAppell %>% filter(EXCLUIU == 0 &
                        VALOR_DANO_MORAL_PREPROCESSED_total == "0")
id_Appell_error <- temp$Filename

temp2 <- dfTrial %>% filter(Filename %in% id_Appell_error) %>%
  select("Filename", "VALOR_DANO_MORAL_PREPROCESSED_total")

dfAppell$VALOR_DANO_MORAL_PREPROCESSED_total[dfAppell$Filename %in% temp2$Filename] <-
  temp2$VALOR_DANO_MORAL_PREPROCESSED_total[temp2$Filename %in% dfAppell$Filename]

# if EXCLUIU == 1,  VALOR_DANO_MORAL_PREPROCESSED_total must be  0,
temp <-
  dfAppell %>% filter(EXCLUIU == 1 &
                        VALOR_DANO_MORAL_PREPROCESSED_total != "0")
id_Appell_error <- temp$Filename

dfAppell[dfAppell$Filename %in% id_Appell_error, "VALOR_DANO_MORAL_PREPROCESSED_total"] <-
  "0"

saveRDS(dfRep, file = "in/dfRep.Rds")
saveRDS(dfTrial, file = "in/dfTrial.Rds")
saveRDS(dfAppell, file = "in/dfAppell.Rds")

CIDS <- dfRep %>% select("Filename", "CID_GRUPO")

#all with unified CID
dfRep <- readRDS(file = "in/dfRep.Rds")
dfTrial <- readRDS(file = "in/dfTrial.Rds")
dfAppell <- readRDS(file = "in/dfAppell.Rds")

temp_1 <-
  dfRep %>% select(Filename, VALOR_DANO_MORAL_PREPROCESSED_total)
temp_1$document <- "R"
colnames(temp_1) <- c("Filename", "value", "document")
temp_2 <-
  dfTrial %>% select(Filename, VALOR_DANO_MORAL_PREPROCESSED_total)
temp_2$document <- "1a"
colnames(temp_2) <- c("Filename", "value", "document")
temp_3 <-
  dfAppell %>% select(Filename, VALOR_DANO_MORAL_PREPROCESSED_total)
temp_3$document <- "2a"
colnames(temp_3) <- c("Filename", "value", "document")

dfRepTrialAppell_CIGgrouped_dm <- rbind(temp_1, temp_2, temp_3)

omitted_val <-
  dfRepTrialAppell_CIGgrouped_dm %>% filter(document == "R" &
                                              value == "0")

saveRDS(dfRepTrialAppell_CIGgrouped_dm, file = "in/dfRepTrialAppell_CIGgrouped_dm.Rds")


# splitCID

dfRepbyCID <- dfRep %>%
  mutate(CID_GRUPO = strsplit(as.character(CID_GRUPO), ",")) %>%
  unnest(CID_GRUPO)


dfTrial_temp <- right_join(dfTrial, CIDS, "Filename")

dfTrialbyCID <- dfTrial_temp %>%
  mutate(CID_GRUPO = strsplit(as.character(CID_GRUPO), ",")) %>%
  unnest(CID_GRUPO)

dfAppell_temp <- left_join(dfAppell, CIDS, "Filename")

dfAppellbyCID <- dfAppell_temp %>%
  mutate(CID_GRUPO = strsplit(as.character(CID_GRUPO), ",")) %>%
  unnest(CID_GRUPO)

saveRDS(dfRepbyCID, file = "in/dfRepbyCID.Rds")
saveRDS(dfTrialbyCID, file = "in/dfTrialbyCID.Rds")
saveRDS(dfAppellbyCID, file = "in/dfAppellbyCID.Rds")

dfAppellExcluiu <-
  dfAppellbyCID %>% filter(EXCLUIU == 1) %>% select(Filename)

# DANOS MORAIS - Moral Damage #

dfRepbyCID <- readRDS(file = "in/dfRepbyCID.Rds")
dfTrialbyCID <- readRDS(file = "in/dfTrialbyCID.Rds")
dfAppellbyCID <- readRDS(file = "in/dfAppellbyCID.Rds")

dfCIDS <- read.csv(file = here('in', "CID-10-CAPITULOS.CSV"),
                   sep = ";")
cids <- as.character(dfCIDS$DESCRICAO_VISUALIZACAO)
names(cids) <- as.character(dfCIDS$NUMCAP)
cids["-1"] <- c("Indefinido")
cids["0"] <- c("Não informado")

c(cids, setNames("Indefinido", "-1"))
c(cids, setNames("Não informado", "0"))


# replace CID values with the appropriate name
dfRepbyCID$CID_NOME <- cids[dfRepbyCID$CID_GRUPO]

dfTrialbyCID$CID_NOME <- cids[dfTrialbyCID$CID_GRUPO]

dfAppellbyCID$CID_NOME <- cids[dfAppellbyCID$CID_GRUPO]

# only Lower cases instance by CID
dfJustFirst <- dfTrialbyCID %>%
  filter(Filename %in% dfRepbyCID$Filename &
           !(Filename %in% dfAppellbyCID$Filename))
temp <- dfJustFirst %>% group_by(CID_GRUPO) %>% tally()

# appeallate casesc
dfWithSecond <- dfTrialbyCID %>%
  filter(Filename %in% dfRepbyCID$Filename &
           Filename %in% dfAppellbyCID$Filename)
temp <- dfWithSecond %>% group_by(CID_GRUPO) %>% tally()


dfRepbyCID_dm <-
  dfRepbyCID %>% select("Filename",
                        "VALOR_DANO_MORAL_PREPROCESSED_total",
                        "CID_GRUPO",
                        "CID_NOME")
dfRepbyCID_dm$document <- "R"
colnames(dfRepbyCID_dm) <-
  c(
    "Filename",
    "VALOR_DANO_MORAL_PREPROCESSED_total",
    "CID_GRUPO",
    "CID_NOME",
    "document"
  )

dfTrialbyCID_dm <-
  dfTrialbyCID %>% select("Filename",
                          "VALOR_DANO_MORAL_PREPROCESSED_total",
                          "CID_NOME",
                          "CID_GRUPO")
dfTrialbyCID_dm$document <- "1a"
documents_trial_no_dn <-
  dfTrialbyCID %>% filter(VALOR_DANO_MORAL_PREPROCESSED_total == "0")

dfAppellbyCID_dm <-
  dfAppellbyCID %>% select("Filename",
                           "VALOR_DANO_MORAL_PREPROCESSED_total",
                           "CID_NOME",
                           "CID_GRUPO")
dfAppellbyCID_dm$document <- "2a"

saveRDS(dfAppellbyCID_dm, file = "in/dfAppellbyCID_dm.Rds")


dfRepTrialAppell_dm <-
  rbind(dfRepbyCID_dm, dfTrialbyCID_dm, dfAppellbyCID_dm)

dfRepTrialAppell_dm <-
  dfRepTrialAppell_dm %>% gather(key = "type",
                                 value = "value",
                                 -c(Filename, CID_GRUPO, CID_NOME, document))

dfRepTrialAppell_dm$value <- as.numeric(dfRepTrialAppell_dm$value)


saveRDS(dfRepTrialAppell_dm, file = "in/dfRepTrialAppell_dm.Rds")
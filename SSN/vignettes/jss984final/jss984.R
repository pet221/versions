### R code from vignette source 'jss984.Rnw'

###################################################
### code chunk number 1: jss984.Rnw:143-147
###################################################
## Code to run in the background
set.seed(210112)
options(prompt = "R> ", continue = "+  ", width = 70, useFancyQuotes = FALSE)
Stangle("jss984.Rnw") ## Dump all R code to a file


###################################################
### code chunk number 2: jss984.Rnw:195-196
###################################################
library("SSN")


###################################################
### code chunk number 3: jss984.Rnw:199-202
###################################################
file.copy(system.file("lsndata/MiddleFork04.ssn", package = "SSN"),
  to = tempdir(), recursive = TRUE, copy.mode = FALSE)
setwd(tempdir())


###################################################
### code chunk number 4: jss984.Rnw:724-725 (eval = FALSE)
###################################################
## importSSN(Path, predpts = NULL, o.write = FALSE)


###################################################
### code chunk number 5: jss984.Rnw:733-735
###################################################
mf04p <- importSSN("./MiddleFork04.ssn",
   predpts = "pred1km")


###################################################
### code chunk number 6: jss984.Rnw:751-753
###################################################
mf04p <- importPredpts(mf04p, "Knapp", "ssn")
mf04p <- importPredpts(mf04p, "CapeHorn", "ssn")


###################################################
### code chunk number 7: jss984.Rnw:801-802 (eval = FALSE)
###################################################
## additive.function(mf04p, VarName, afvName)


###################################################
### code chunk number 8: jss984.Rnw:815-816
###################################################
names(mf04p@data)


###################################################
### code chunk number 9: jss984.Rnw:820-821
###################################################
head(mf04p@data[, c("h2oAreaKm2", "afvArea")])


###################################################
### code chunk number 10: jss984.Rnw:825-826
###################################################
mf04p <- additive.function(mf04p, "h2oAreaKm2", "computed.afv")


###################################################
### code chunk number 11: jss984.Rnw:830-831
###################################################
names(mf04p@data)


###################################################
### code chunk number 12: jss984.Rnw:835-838
###################################################
head(mf04p@data[, c("h2oAreaKm2",
   "afvArea", "computed.afv")])
head(getSSNdata.frame(mf04p)[, c("afvArea", "computed.afv")])


###################################################
### code chunk number 13: jss984.Rnw:880-884
###################################################
createDistMat(mf04p, predpts = "Knapp", o.write = TRUE,
	amongpreds = TRUE)
createDistMat(mf04p, predpts = "CapeHorn", o.write = TRUE,
	amongpreds = TRUE)


###################################################
### code chunk number 14: jss984.Rnw:922-923
###################################################
names(mf04p)


###################################################
### code chunk number 15: LoadData
###################################################
plot(mf04p, lwdLineCol = "afvArea", lwdLineEx = 10, lineCol = "blue",
   pch = 19, xlab = "x-coordinate (m)", ylab = "y-coordinate (m)",
   asp = 1)


###################################################
### code chunk number 16: plotSpatialStreamNetwork
###################################################
brks <- plot(mf04p, "Summer_mn", lwdLineCol = "afvArea",
   lwdLineEx = 15, lineCol = "black", xlab =  "x-coordinate" ,
   ylab =  "y-coordinate", asp=1 )


###################################################
### code chunk number 17: Torgegram
###################################################
mf04.Torg <- Torgegram(mf04p, "Summer_mn", nlag = 20, maxlag = 50000)
plot(mf04.Torg)


###################################################
### code chunk number 18: GauModel0
###################################################
mf04.glmssn0 <- glmssn(Summer_mn ~ ELEV_DEM + SLOPE, mf04p,
   CorModels = NULL, use.nugget = TRUE)
summary(mf04.glmssn0)


###################################################
### code chunk number 19: lm0
###################################################
summary(lm(Summer_mn ~ ELEV_DEM + SLOPE, getSSNdata.frame(mf04p)))


###################################################
### code chunk number 20: GauModel1
###################################################
mf04.glmssn1 <- glmssn(Summer_mn ~ ELEV_DEM + SLOPE, mf04p,
   CorModels = c("Exponential.tailup", "Exponential.taildown",
      "Exponential.Euclid"), addfunccol = "afvArea")
summary(mf04.glmssn1)


###################################################
### code chunk number 21: BinModel1
###################################################
mf04.glmssnBin <- glmssn(MaxOver20 ~ ELEV_DEM + SLOPE, mf04p,
  CorModels = c("Mariah.tailup", "Spherical.taildown"),
  family = "binomial", addfunccol = "afvArea")
summary(mf04.glmssnBin)


###################################################
### code chunk number 22: PoiModel1
###################################################
mf04.glmssnPoi <- glmssn(C16 ~ ELEV_DEM + SLOPE, mf04p,
  CorModels = c("LinearSill.tailup", "LinearSill.taildown"),
  family = "poisson", addfunccol = "afvArea")
summary(mf04.glmssnPoi)


###################################################
### code chunk number 23: Model1
###################################################
mf04.resid1 <- residuals(mf04.glmssn1)
names( getSSNdata.frame(mf04.resid1) )
plot(mf04.resid1)


###################################################
### code chunk number 24: ResidHist
###################################################
par(mfrow = c(1, 2))
hist(mf04.resid1)
hist(mf04p, "Summer_mn")


###################################################
### code chunk number 25: jss984.Rnw:1154-1159
###################################################
ObsDFr <- getSSNdata.frame(mf04.resid1)
ObsDF <- getSSNdata.frame(mf04p)
indOutlier <- ObsDFr["_resid_"] < -3
ObsDF[indOutlier, "Summer_mn"] <- NA
mf04c <- putSSNdata.frame(ObsDF, mf04p)


###################################################
### code chunk number 26: jss984.Rnw:1164-1168
###################################################
mf04c.glmssn0 <- glmssn(Summer_mn ~ ELEV_DEM + SLOPE, mf04c,
   CorModels = c("Exponential.tailup", "Exponential.taildown",
   "Exponential.Euclid"), addfunccol = "afvArea", EstMeth = "ML")
summary(mf04c.glmssn0)


###################################################
### code chunk number 27: jss984.Rnw:1173-1177
###################################################
mf04c.glmssn1 <- glmssn(Summer_mn ~ ELEV_DEM, mf04c,
   CorModels = c("Exponential.tailup", "Exponential.taildown"),
   addfunccol = "afvArea", EstMeth = "ML")
summary(mf04c.glmssn1)


###################################################
### code chunk number 28: LOOCV
###################################################
cv.out <- CrossValidationSSN(mf04c.glmssn1)
par(mfrow = c(1, 2))
plot(mf04c.glmssn1$sampinfo$z,
   cv.out[, "cv.pred"], pch = 19,
   xlab = "Observed Data", ylab = "LOOCV Prediction")
abline(0, 1)
plot( na.omit( getSSNdata.frame(mf04c)[, "Summer_mn"]),
   cv.out[, "cv.se"], pch = 19,
   xlab = "Observed Data", ylab = "LOOCV Prediction SE")


###################################################
### code chunk number 29: LOOCVSummary
###################################################
CrossValidationStatsSSN(mf04c.glmssn1)


###################################################
### code chunk number 30: jss984.Rnw:1231-1233
###################################################
GR2(mf04c.glmssn1)
varcomp(mf04c.glmssn1)


###################################################
### code chunk number 31: jss984.Rnw:1250-1252
###################################################
AIC(mf04c.glmssn0)
AIC(mf04c.glmssn1)


###################################################
### code chunk number 32: jss984.Rnw:1260-1275
###################################################
mf04c.glmssn1 <- glmssn(Summer_mn ~ ELEV_DEM, mf04c,
   CorModels = c("Exponential.tailup", "Exponential.taildown"),
   addfunccol = "afvArea")
mf04c.glmssn2 <- glmssn(Summer_mn ~ ELEV_DEM,  mf04c,
   CorModels = c("LinearSill.tailup", "Mariah.taildown"),
   addfunccol = "afvArea")
mf04c.glmssn3 <- glmssn(Summer_mn ~ ELEV_DEM , mf04c,
   CorModels =  c("Mariah.tailup", "LinearSill.taildown"),
   addfunccol = "afvArea")
mf04c.glmssn4 <- glmssn(Summer_mn ~ ELEV_DEM, mf04c,
   CorModels = c("Spherical.tailup", "Spherical.taildown"),
   addfunccol = "afvArea")
mf04c.glmssn5 <- glmssn(Summer_mn ~ ELEV_DEM, mf04c,
   CorModels = "Exponential.Euclid",
   addfunccol = "afvArea")


###################################################
### code chunk number 33: jss984.Rnw:1283-1287
###################################################
options(digits = 4)
InfoCritCompare(list(mf04c.glmssn1, mf04c.glmssn2,
   mf04c.glmssn3, mf04c.glmssn4, mf04c.glmssn5))
options(digits = 7)


###################################################
### code chunk number 34: jss984.Rnw:1299-1300
###################################################
summary(mf04c.glmssn2)


###################################################
### code chunk number 35: Residuals
###################################################
mf04c.resid2 <- residuals(mf04c.glmssn2)
mf04c.resid2.cv.std <-
    getSSNdata.frame(mf04c.resid2)[, "_resid.crossv_"] /
    getSSNdata.frame(mf04c.resid2)[, "_CrossValStdErr_"]
hist(mf04c.resid2.cv.std)


###################################################
### code chunk number 36: TorgRes
###################################################
plot(Torgegram(mf04c.resid2, "_resid_", nlag = 8, maxlag = 25000))


###################################################
### code chunk number 37: Preds1
###################################################
mf04c.pred1km <- predict(mf04c.glmssn4, "pred1km")
plot(mf04c.pred1km, SEcex.max = 1, SEcex.min = .5/3*2,
     breaktype = "user", brks = brks)


###################################################
### code chunk number 38: Preds2
###################################################
plot(mf04c, "Summer_mn", pch = 1, cex = 3,
   xlab = "x-coordinate", ylab = "y-coordinate",
   xlim = c(-1511000,-1500000), ylim = c(2525000,2535000))
mf04c.glmssn4.Knapp <- predict(mf04c.glmssn4, "Knapp")
plot(mf04c.glmssn4.Knapp, "Summer_mn", add = TRUE,
   xlim = c(-1511000,-1500000), ylim = c(2525000,2535000))


###################################################
### code chunk number 39: jss984.Rnw:1415-1417
###################################################
mf04c.glmssn4.BPKnapp <- BlockPredict(mf04c.glmssn4, "Knapp")
mf04c.glmssn4.BPKnapp


###################################################
### code chunk number 40: jss984.Rnw:1421-1423
###################################################
mf04c.glmssn4.BPCapeHorn <- BlockPredict(mf04c.glmssn4, "CapeHorn")
mf04c.glmssn4.BPCapeHorn


###################################################
### code chunk number 41: jss984.Rnw:1436-1439
###################################################
mf04c.missingobs <- predict(mf04c.glmssn4, "_MissingObs_")
getPreds(mf04c.missingobs, pred.type = "pred")
with(getSSNdata.frame(mf04p), Summer_mn[pid==29])


###################################################
### code chunk number 42: jss984.Rnw:1486-1488 (eval = FALSE)
###################################################
## createSSN(n, obsDesign, predDesign = noPoints, path,
##    importToR = FALSE, treeFunction = igraphKamadaKawai)


###################################################
### code chunk number 43: SimIterative
###################################################
set.seed(12)
iterative.ssn <- createSSN(n = c(30, 10),
   obsDesign = binomialDesign(c(10,10)),
   importToR = TRUE, path = "./SimIterative.ssn",
   treeFunction = iterativeTreeLayout)
plot(iterative.ssn, lwdLineCol = "addfunccol", lwdLineEx = 8,
   lineCol = "blue", cex = 2, xlab = "x-coordinate",
   ylab = "y-coordinate", pch = 1)


###################################################
### code chunk number 44: SimSSN1
###################################################
set.seed(101)
raw.ssn <- createSSN(n = c(10, 10, 10),
   obsDesign = binomialDesign(c(40, 40, 40)),
   predDesign = systematicDesign(c(0.2, 0.4, 0.8)), importToR = TRUE,
   path = "./raw.ssn")
plot(raw.ssn, lwdLineCol = "addfunccol", lwdLineEx = 8,
   lineCol = "blue", cex = 2, xlab = "x-coordinate",
   ylab = "y-coordinate", pch = 1)
plot(raw.ssn, PredPointsID = "preds", add = TRUE, cex = .5, pch = 19,
   col = "green")


###################################################
### code chunk number 45: SimHardcore
###################################################
set.seed(13)
hardcore.ssn <- createSSN(n = c(10, 10),
   obsDesign = hardCoreDesign(c(200, 200), c(0.2, 0.4)),
   importToR = TRUE, path = "./SimHardcore.ssn")
plot(hardcore.ssn, lwdLineCol = "addfunccol", lwdLineEx = 8,
   lineCol = "blue", cex = 2, xlab = "x-coordinate",
   ylab = "y-coordinate", pch = 1)
plot(hardcore.ssn, PredPointsID = NULL, add = TRUE, cex = .5,
   pch = 19, col = "green")


###################################################
### code chunk number 46: jss984.Rnw:1624-1625
###################################################
createDistMat(raw.ssn, "preds", o.write=TRUE, amongpred = TRUE)


###################################################
### code chunk number 47: jss984.Rnw:1638-1640
###################################################
rawDFobs <- getSSNdata.frame(raw.ssn, "Obs")
rawDFpred <- getSSNdata.frame(raw.ssn, "preds")


###################################################
### code chunk number 48: jss984.Rnw:1645-1649
###################################################
rawDFobs[,"X1"] <- rnorm(length(rawDFobs[,1]))
rawDFpred[,"X1"] <- rnorm(length(rawDFpred[,1]))
rawDFobs[,"X2"] <- rnorm(length(rawDFobs[,1]))
rawDFpred[,"X2"] <- rnorm(length(rawDFpred[,1]))


###################################################
### code chunk number 49: jss984.Rnw:1654-1658
###################################################
rawDFobs[,"F1"] <- as.factor(sample.int(4,length(rawDFobs[,1]),
   replace = TRUE))
rawDFpred[,"F1"] <- as.factor(sample.int(4,length(rawDFpred[,1]),
   replace = TRUE))


###################################################
### code chunk number 50: jss984.Rnw:1664-1672
###################################################
rawDFobs[,"RE1"] <- as.factor(sample(1:3,length(rawDFobs[,1]),
   replace = TRUE))
rawDFobs[,"RE2"] <- as.factor(sample(1:4,length(rawDFobs[,1]),
   replace = TRUE))
rawDFpred[,"RE1"] <- as.factor(sample(1:3,length(rawDFpred[,1]),
   replace = TRUE))
rawDFpred[,"RE2"] <- as.factor(sample(1:4,length(rawDFpred[,1]),
   replace = TRUE))


###################################################
### code chunk number 51: jss984.Rnw:1677-1679
###################################################
names(rawDFobs)
names(rawDFpred)


###################################################
### code chunk number 52: jss984.Rnw:1695-1703
###################################################
set.seed(102)
sim.out <- SimulateOnSSN(raw.ssn, ObsSimDF = rawDFobs,
   PredSimDF = rawDFpred, PredID = "preds",
   formula = ~ X1 + X2 + F1, coefficients = c(10,1,0,-2,0,2),
   CorModels = c("LinearSill.tailup", "Mariah.taildown",
   "Exponential.Euclid", "RE1", "RE2"), use.nugget = TRUE,
   CorParms = c(3, 10, 2, 10, 1, 5, 1, .5, .1),
   addfunccol = "addfunccol")


###################################################
### code chunk number 53: jss984.Rnw:1733-1734
###################################################
with(rawDFobs, colnames(model.matrix( ~ X1 + X2 + F1)))


###################################################
### code chunk number 54: jss984.Rnw:1758-1760
###################################################
sim.out$FixedEffects
sim.out$CorParms


###################################################
### code chunk number 55: jss984.Rnw:1764-1765
###################################################
sim.ssn <- sim.out$ssn.object


###################################################
### code chunk number 56: SimSSN2
###################################################
plot(sim.ssn, "Sim_Values",
   xlab = "x-coordinate", ylab = "y-coordinate",
   cex = 1.5)


###################################################
### code chunk number 57: jss984.Rnw:1789-1791
###################################################
simDFobs <- getSSNdata.frame(sim.ssn, "Obs")
simDFpred <- getSSNdata.frame(sim.ssn, "preds")


###################################################
### code chunk number 58: jss984.Rnw:1796-1799
###################################################
simpreds <- simDFpred[,"Sim_Values"]
simDFpred[,"Sim_Values"] <- NA
sim.ssn <- putSSNdata.frame(simDFpred, sim.ssn, "preds")


###################################################
### code chunk number 59: jss984.Rnw:1804-1808
###################################################
glmssn.out <- glmssn(Sim_Values ~ X1 + X2 + F1, sim.ssn,
   CorModels = c("LinearSill.tailup", "Mariah.taildown",
   "Exponential.Euclid", "RE1", "RE2"),
   addfunccol = "addfunccol")


###################################################
### code chunk number 60: jss984.Rnw:1812-1813
###################################################
summary(glmssn.out)


###################################################
### code chunk number 61: SimTvP
###################################################
glmssn.pred <- predict(glmssn.out,"preds")
predDF <- getSSNdata.frame(glmssn.pred, "preds")
plot(simpreds, predDF[,"Sim_Values"], xlab = "True",
   ylab = "Predicted", pch = 19)



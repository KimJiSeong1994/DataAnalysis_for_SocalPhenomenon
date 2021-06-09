library(tidyverse)

df = read.csv("./Downloads/w2v_weight_df.csv")[, -1]
survey

rownames(df) = df$vocabs
df = df %>% select(-vocabs)
# 
# rownames(survey) = survey$words
# survey = survey %>% select(-words)

norm_vec = function(x) sqrt(sum(x^2))
dot = function(x,y) (sum(x*y))
cos = function(x,y) dot(x,y)/norm_vec(x)/norm_vec(y)
nrm = function(x) x/norm_vec(x)
dimension<-function(x,y) nrm(nrm(x)-nrm(y))

cdfm = as.matrix(df)
cdfmn = t(apply(cdfm,1,nrm))

ant_pairs_aff = read.csv("./Downloads/affluence_pairs.csv")
ant_pairs_gen = read.csv("./Downloads/gender_pairs.csv")
ant_pairs_con = read.csv("./Downloads/con_pairs.csv")

word_dims = matrix(NA, nrow(ant_pairs_aff), 500)
make_dim <- function(embedding,pairs){
  word_dims <- data.frame(matrix(NA, nrow(pairs), 500))
  for (j in 1 : nrow(pairs)) {
    rp_word1 <- pairs[j, 1]
    rp_word2 <- pairs[j, 2]
    tryCatch(word_dims[j,] <- dimension(embedding[rp_word1, ], embedding[rp_word2, ]),
             error = function(e){ })
  }
  dim_ave <- colMeans(word_dims, na.rm = TRUE)
  dim_ave_n <- nrm(dim_ave)
  return(dim_ave_n)
}

aff_dim <- make_dim(df, ant_pairs_aff)
gender_dim <- make_dim(df, ant_pairs_gen)
con_dim <- make_dim(df, ant_pairs_con)

cos(aff_dim, gender_dim)
cos(aff_dim, con_dim)
cos(gender_dim, con_dim)

aff_proj <- cdfmn %*% aff_dim
gender_proj <- cdfmn %*% gender_dim
con_proj <- cdfmn %*% con_dim

projections_df <- cbind(aff_proj, gender_proj, con_proj)
colnames(projections_df) <- c("aff_proj", "gender_proj", "con_proj")

projections_sub <- subset(projections_df, rownames(projections_df) %in% rownames(survey))
colnames(projections_sub) <- c("aff_proj","gender_proj", "con_proj")
survey_proj <- merge(survey, projections_sub, by = 0)

cor(survey_proj$class, survey_proj$aff_proj)
cor(survey_proj$gender, survey_proj$gender_proj)
cor(survey_proj$policy, survey_proj$con_proj)

wlist = str_remove(rownames(survey), "\\s")
wlist = str_remove(wlist, "\\([^)]*\\)")
wlist = c('민주당', '국민의힘', '정의당', '김대중', '노무현', '김영삼', '박근혜', '이명박')

data.frame(projections_df[rownames(projections_df) %in% wlist, ]) %>% 
  ggplot(aes(x = gender_proj, y = aff_proj, label = rownames(projections_df[rownames(projections_df) %in% wlist, ]))) +
  geom_text(family = "AppleGothic", hjust = -0.15, vjust = -0.15, size = 3.5) +
  geom_jitter(col = "blue", size = 1) +
  theme_bw() +
  ylim(-.15,.15) +
  xlim(-.15,.15)
  



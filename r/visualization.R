library(DBI)
library(RPostgres)
library(dplyr)
library(jsonlite)

con <- dbConnect(
  RPostgres::Postgres(),
  host = "localhost",
  port = "5432",
  dbname = "prototype",
  user = "postgres",
  password = rstudioapi::askForPassword("Database password")
)

sequences <- dbGetQuery(con, "SELECT * FROM sequence;")
head(sequences)

sequences <- dbGetQuery(con, "SELECT * FROM sequence;")
nrow(sequences)

seq_by_pathogen <- dbGetQuery(con, "
                              SELECT
                                  p.scientific_name AS pathogen_name,
                                  s.sequence_length,
                                  s.gc_content
                              FROM sequence s
                              JOIN organism o ON s.organism_id = o.organism_id
                              JOIN pathogen p ON o.pathogen_id = p.pathogen_id;
                            ")
head(seq_by_pathogen)

library(ggplot2)


pathogen_counts <- seq_by_pathogen %>%
  count(pathogen_name, name = "sequence_count")


pathogen_counts

ggplot(pathogen_counts, aes(x = pathogen_name, y = sequence_count)) +
  geom_col(fill = "pink") +
  labs(
    title = "Sequences Ingested per Pathogen",
    x = "Pathogen",
    y = "Number of Sequences"
  ) +
  theme_minimal()

ggplot(seq_by_pathogen, aes(x = pathogen_name, y = gc_content)) +
  geom_boxplot(fill = "red") +
  labs(
    title = "GC Content Distribution by Pathogen",
    x = "Pathogen",
    y = "GC Content (%)"
  ) +
  theme_minimal()

seq_by_pathogen %>%
  group_by(pathogen_name) %>%
  summarise(
    min_gc = min(gc_content, na.rm = TRUE),
    median_gc = median(gc_content, na.rm = TRUE),
    max_gc = max(gc_content, na.rm = TRUE),
    n = n()
  )

seq_by_pathogen <- seq_by_pathogen %>%
  mutate(scale = ifelse(sequence_length >= 1000, "genome-scale", "fragment"))
         
seq_by_pathogen %>%
  count(pathogen_name, scale)

ggplot(seq_by_pathogen, aes(x = pathogen_name, y = gc_content, fill = scale)) +
  geom_boxplot() +
  labs(
    title = "GC Content by Pathogen and Sequence Scale",
    x = "Pathogen",
    y = "GC Content (%)",
    fill = "Sequence Type"
  ) +
  theme_minimal()
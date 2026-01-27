import { defineCollection, z } from "astro:content";

// Articles collection - news articles from daily pipeline
const articles = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    title_vi: z.string().optional(),
    source: z.string(),
    url: z.string().url(),
    topic: z.string(),
    date: z.string(), // YYYY-MM-DD
    excerpt: z.string(),
    excerpt_vi: z.string().optional(),
    number: z.number(), // Playlist order within topic
    publishDate: z.coerce.date().optional(),
  }),
});

// Daily summaries - overview for each day
const dailies = defineCollection({
  type: "content",
  schema: z.object({
    date: z.string(),
    title: z.string(),
    title_vi: z.string().optional(),
    articleCount: z.number(),
    topicCounts: z.record(z.number()),
    publishDate: z.coerce.date().optional(),
  }),
});

// Team collection (from Astroship template)
const team = defineCollection({
  type: "content",
  schema: z.object({
    draft: z.boolean(),
    name: z.string(),
    title: z.string(),
    avatar: z.object({
      src: z.string(),
      alt: z.string(),
    }),
    publishDate: z.string().transform((str) => new Date(str)),
  }),
});

export const collections = {
  articles,
  dailies,
  team
};
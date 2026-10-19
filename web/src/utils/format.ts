export const formatDate = (iso: string) =>
  new Intl.DateTimeFormat("id-ID", {
    dateStyle: "long",
    timeZone: "Asia/Jakarta",
  }).format(new Date(iso));

export const stripTags = (html: string) =>
  html
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();

export const excerpt = (html: string, max = 160) => {
  const t = stripTags(html);
  return t.length > max ? t.slice(0, max).replace(/\s+\S*$/, "") + "…" : t;
};

export const readingTime = (html: string) =>
  Math.max(1, Math.round(stripTags(html).split(" ").length / 200));

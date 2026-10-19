import { createClient } from "@supabase/supabase-js";

export interface Article {
  id: string;
  slug: string;
  title: string;
  content_html: string;
  source_link: string;
  source_name: string | null;
  published_at: string;
}

// Versi ringan untuk halaman daftar (tanpa content_html)
export type ArticleSummary = Omit<Article, "content_html">;

const url = import.meta.env.PUBLIC_SUPABASE_URL;
const key = import.meta.env.PUBLIC_SUPABASE_ANON_KEY;

if (!url || !key) {
  throw new Error(
    "PUBLIC_SUPABASE_URL / PUBLIC_SUPABASE_ANON_KEY belum diset (cek web/.env atau env Cloudflare Pages).",
  );
}

export const supabase = createClient(url, key, {
  auth: { persistSession: false },
});

// ganti SUMMARY_COLUMNS dan return type getArticles
const SUMMARY_COLUMNS = "*";

export async function getArticles(limit = 50): Promise<Article[]> {
  const { data, error } = await supabase
    .from("articles")
    .select(SUMMARY_COLUMNS)
    .order("published_at", { ascending: false })
    .limit(limit);
  if (error) throw new Error(`getArticles gagal: ${error.message}`);
  return data ?? [];
}

export async function getAllArticles(): Promise<Article[]> {
  return getArticles(1000);
}

export async function getArticleBySlug(slug: string): Promise<Article | null> {
  const { data, error } = await supabase
    .from("articles")
    .select("*")
    .eq("slug", slug)
    .maybeSingle();

  if (error) throw new Error(`getArticleBySlug gagal: ${error.message}`);
  return data;
}

// Untuk getStaticPaths() dan sitemap
export async function getAllSlugs(): Promise<
  Pick<Article, "slug" | "published_at">[]
> {
  const { data, error } = await supabase
    .from("articles")
    .select("slug, published_at")
    .order("published_at", { ascending: false });

  if (error) throw new Error(`getAllSlugs gagal: ${error.message}`);
  return data ?? [];
}

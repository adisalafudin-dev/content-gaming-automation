import sanitizeHtml from "sanitize-html";

export function cleanHtml(html: string) {
  return sanitizeHtml(html, {
    allowedTags: [
      "p",
      "h2",
      "h3",
      "h4",
      "ul",
      "ol",
      "li",
      "strong",
      "em",
      "a",
      "blockquote",
      "br",
      "table",
      "thead",
      "tbody",
      "tr",
      "th",
      "td",
    ],
    allowedAttributes: { a: ["href"] },
    allowedSchemes: ["http", "https"],
    transformTags: {
      h1: "h2", // satu h1 per halaman
      a: sanitizeHtml.simpleTransform("a", {
        rel: "noopener nofollow",
        target: "_blank",
      }),
    },
  });
}

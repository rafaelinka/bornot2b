# B(ornot)2B — How business gets done.

A Saturday journal exploring how companies buy, sell and work together around the world.

## Public edition

Owner-approved English edition 01 and voluntary Boosty support were approved for public release on October 31, 2026.

- Main site: https://bornot2b.com/ — English by default.
- Russian edition: https://bornot2b.com/ru/.
- Permanent issue pages: `/issue-01/` through `/issue-05/`, with Russian counterparts under `/ru/`. The archive shows each issue as an illustrated cover at `/archive/`.
- Both homepages are permanent journal pages with their own canonical URLs, a cover linking directly to the latest numbered issue, and selected article links. The build preserves these pages instead of replacing them with an issue copy.
- Each numbered issue and full analysis retains its permanent address after a newer issue appears. The build requires matching English and Russian pages for every issue.
- Each reader page links to its language counterpart.
- One-time support: https://boosty.to/bornot2b/donate. All stories remain free.

Boosty Basic verification is complete and a primary RUB payout card is linked. Real payments and payouts have not been tested.

## Editorial approach

Primary-source facts, company claims and editorial interpretation are distinguished. Text and illustrations are prepared with AI assistance. No independent human fact-check or English copyedit is claimed. See docs/editorial-format.md.

The site uses system fonts; it distributes no font files. Raw book files, internal research notes and credentials are excluded. Third-party rights in books and company marks remain with their owners. Rights clearance of third-party imagery should not be assumed from AI generation.

## Build and publication

```sh
python3 scripts/build.py --base-url https://bornot2b.com
python3 scripts/validate.py --base-url https://bornot2b.com
```

Validation checks independent self-canonical homepages, reciprocal language links, direct links to the latest issue, and inclusion of both homepages in the sitemap, in addition to existing reader and archive checks.

GitHub Actions builds from source. Pushes only run checks. Publication is manual through `Publish approved issue` on main, after owner approval. HTTPS is enforced for the custom domain.

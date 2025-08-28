# Privacy & Data Handling Policy

**Last Updated**: January 2025  
**Effective Date**: April 2024

This document explains how BookScrapeDB_Recommends collects, processes, stores, and protects data.

---

## Overview

BookScrapeDB_Recommends is first and foremost an **educational and research platform** that processes publicly available literature data to generate analytics, recommendations, and market insights. This policy describes our data practices.
<br>

> [!WARNING]  
> Any deployment or production use is within ToS,regulatory compliance and through EXPLICIT AGREEMENT with platforms scraped/mined at larger scale.

---

## 1. What Data is Collected

### 1.1 From Web Sources (Publicly Available)

**Goodreads (Possibly restricted by new Amazon LLC ToS VS deprecated 2021 API, need explicit agreement in prod):**
- Book metadata (titles, ISBNs, publication dates, descriptions, genres)
- Author information (names, biographies, works)
- User reviews (text content, ratings, review dates)
- Reviewer following and user profiles (usernames, reading statistics, public profile data)
- Reading lists and bookshelves (publicly shared collections)
- External links / platforms embedded in any of the above

**Google Books (Restricted by scale, review Google LLC compliance):**
- Google user data, Google reviews/Google Books user generated content
- Bibliographic metadata (titles, authors, publishers, ISBNs)
- Book descriptions and subject classifications
- Cover images and thumbnails
- Retail and list price information
- Availability and format data
- External links / platforms embedded in any of the above

**OpenLibrary:**
- Catalog data and subject headings
- Community-contributed metadata
- Author and work information
- Public domain book data
- External links / platforms embedded in any of the above

**ISBNdb:**
- Market and pricing
- Retailers, Supply chain, publishers, licensors
- Authoritative ISBN validation
- Book, Catalog and Series specific Editions validation

**External Sources:**
- Independently published catalogs linked from the above platforms
- Attribution data from external literary databases
- Cross-referenced ISBN data from ISBNdb and similar services

### 1.2 From APIs (With Proper Authorization)

- **Google Books API**: Official access with API key, rate limiting, and proper attribution
- **OpenLibrary API**: Open data initiative (public domain)
- **ISBNdb API**: Subscription-based access for ISBN validation and pricing

### 1.3 Data NOT Collected

This project does **NOT** collect:
- ❌ Email addresses or contact information
- ❌ Passwords or authentication credentials
- ❌ IP addresses or device identifiers
- ❌ Payment information
- ❌ Private messages or non-public content
- ❌ Data behind authentication walls or paywalls

---

## 2. How Data is Processed

### 2.1 User Anonymization

**Reviewer Identities:**
- Usernames are processed during ETL but **anonymized** in database outputs
- No direct mapping between usernames and database IDs is exposed
- Statistical aggregations prevent individual identification

**User Reviews:**
- Review text processed through NLP and sentiment analysis
- Transformed into embeddings, sentiment scores, and statistical models
- Original verbatim text **NOT stored** in final database
- Only aggregated insights retained (e.g., "positive sentiment: 0.85")

**Profile Data:**
- Reading behaviors aggregated into statistical profiles
- Individual reading lists transformed into genre preferences and patterns
- No personally identifiable profiles exported or visualized

### 2.2 AI/ML Processing

**Large Language Models (LLMs):**
- Used for sentiment analysis and thematic categorization
- Review text processed transiently (not permanently stored by models)
- No user identification or profiling beyond reading preferences

**Retrieval-Augmented Generation (RAG):**
- Hybrid Vector+Graph embeddings for book recommendations
- User behavior patterns encoded as anonymous vectors
- Graph analytics identify community clusters without individual tracking

**Natural Language Processing (NLP):**
- Text mining on publicly available review content
- Topic modeling and sentiment extraction
- Aggregated insights only (not individual-level analysis)

### 2.3 Graph Analytics

**Network Analysis:**
- PageRank and centrality algorithms identify influential books/authors
- Community detection algorithms find reader clusters
- All visualizations use anonymized nodes (no usernames displayed)

---

## 3. Data Storage & Retention

### 3.1 Local Storage

**Raw Data:**
- Temporarily stored during ETL processing
- Retained locally for validation and debugging
- Not distributed or shared with third parties

**Processed Data:**
- SQL DML files contain transformed, anonymized data
- Neo4j graph database stores relationship patterns (no PII)
- API response caches stored locally to reduce redundant requests

### 3.2 No Cloud Upload (By Default)

**Important:** This codebase processes data **locally by default**. No raw scraped data is automatically uploaded to cloud services unless explicitly configured by the user.

If deploying to cloud platforms (GCP, AWS, etc.):
- User is responsible for data protection compliance
- Encryption in transit and at rest recommended
- Access controls must be implemented
- Regional data residency requirements must be met

### 3.3 Data Retention

**Development Environment:**
- Raw data: Retained indefinitely for reprocessing
- Cached API responses: Retained to minimize API calls
- Database outputs: Retained as project artifacts

**Users implementing this system:**
- Should define their own retention policies
- Must comply with applicable data protection regulations
- Should implement secure deletion when data is no longer needed

---

## 4. Data Minimization

### 4.1 Collection Principles

**Only Publicly Available Data:**
- No attempts to access private or authenticated content
- Respects platform privacy settings
- Does not scrape content behind login walls

**Purpose Limitation:**
- Data collected only for analytics and recommendation purposes
- No secondary use for advertising, tracking, or surveillance
- No sale or sharing of data with third parties

**Minimal Retention:**
- Only essential data fields retained
- Verbatim review text discarded after NLP processing
- Aggregated insights preferred over granular records

---

## 5. Data Security

### 5.1 Technical Safeguards

**Code Obfuscation:**
- Scraping logic obfuscated to prevent unauthorized replication
- Reduces risk of large-scale Terms of Service violations by bad actors

**Access Controls:**
- Local file system permissions protect raw data
- Database credentials should be stored securely (environment variables)
- API keys never committed to version control

**Rate Limiting:**
- Prevents server overload on source platforms
- Reduces risk of IP bans or service interruptions
- Demonstrates respectful data collection practices

### 5.2 No Security Guarantees

**Important:** This is educational software. The author does NOT guarantee:
- Protection against unauthorized access
- Prevention of data breaches in user implementations
- Security of third-party dependencies
- Compliance with enterprise security standards

**Users are responsible** for implementing appropriate security measures in their deployments.

---

## 6. Compliance with Regulations

### 6.1 GDPR (European Union)

**Legal Basis for Processing:**
- Legitimate interest: Educational research and portfolio demonstration
- Publicly available data: No expectation of privacy for publicly shared reviews

**Data Subject Rights:**
- Right to erasure: Contact maintainer to request data removal
- Right to access: Request copy of processed data related to your content
- Right to object: Contact maintainer to opt-out of data processing

**Limitations:**
- This project processes publicly available data already published by users
- Complete removal requires adjusting privacy settings on source platforms

### 6.2 CCPA (California)

**No Sale of Personal Information:**
- This project does NOT sell user data
- No data sharing with third parties for monetary consideration

**Consumer Rights:**
- Right to know: This policy describes data collection practices
- Right to delete: Contact maintainer for data removal
- Right to opt-out: Adjust privacy settings on source platforms

### 6.3 Other Jurisdictions

Users deploying this system must ensure compliance with:
- Canadian PIPEDA
- Brazilian LGPD
- Australian Privacy Act
- Other applicable data protection laws

**The author is NOT responsible** for compliance in user implementations.

---

## 7. User Rights

### 7.1 If You Are a Goodreads/Platform User

**To request removal of your data:**
1. Contact the maintainer via GitHub with:
   - Your platform username
   - Specific reviews or content to remove
   - Proof of ownership (e.g., link to your profile)
2. Allow 7-14 days for processing
3. Confirm removal after processing

**Note:** This project processes publicly available data. For complete control:
- Adjust privacy settings on source platforms (Goodreads, etc.)
- Delete or make private any content you don't want processed
- Contact source platforms directly for broader removal

### 7.2 If You Are Implementing This Code

**Your obligations:**
- Define your own data retention policies
- Implement user data request procedures
- Comply with applicable privacy regulations
- Provide transparency to users about data practices

---

## 8. Third-Party Services

### 8.1 Data Sharing

**This project does NOT share data with:**
- Advertising networks
- Analytics services (beyond self-hosted analytics)
- Data brokers or aggregators
- Social media platforms (beyond source platforms)

**Exception:** If deploying to cloud platforms (GCP, AWS), user data may be processed by those services according to their privacy policies.

### 8.2 API Providers

**When using official APIs:**
- Google Books API: Subject to [Google Privacy Policy](https://policies.google.com/privacy)
- OpenLibrary API: Subject to Internet Archive privacy practices
- ISBNdb API: Subject to ISBNdb privacy policy

---

## 9. Children's Privacy

This project is **not directed at children under 13** (or 16 in the EU).

- No knowing collection of data from children
- If child data is inadvertently processed, contact maintainer for immediate removal
- Source platforms (Goodreads, ISBN auth, Google Books, etc.) have their own age restrictions

---

## 10. Changes to This Policy

This Privacy Policy may be updated to reflect:
- Changes in data handling practices
- New regulatory requirements
- User feedback and concerns

**Check the "Last Updated" date** at the top of this document regularly.

**Continued use** after policy changes constitutes acceptance of updated terms.

---

## 11. Transparency & Accountability

### 11.1 Open Source

While this is a OSS, restritions apply. All CORE data processing logic is visible in the codebase for transparency, but some code/files are intentionally left out or obfuscated. 
<br>
> [!TIP]
> Request for full access if under collaboration guidelines

### 11.2 No Hidden Data Collection

- No telemetry or tracking in the code
- No hidden API calls to external services
- All data collection is explicitly documented

### 11.3 User Control

Users implementing this system have full control over:
- What data is collected
- How data is processed
- Where data is stored
- When data is deleted

---

## 12. Contact & Data Requests

**For privacy-related inquiries:**
- Open a GitHub issue (for general questions)
- Contact maintainer directly (for data removal requests)
- See ```SECURITY.md```

**GitHub**: @ChiefsBestPal  
**Repository**: https://github.com/ChiefsBestPal/BooksScrapeDatabase_and_Recommender

---

## 13. Disclaimer

**This policy describes the default behavior of the codebase as published.**

Users who modify or deploy this code are responsible for:
- Creating their own privacy policies
- Ensuring compliance with applicable laws
- Implementing appropriate data protections
- Providing transparency to their users

**The author is NOT responsible** for privacy practices in third-party implementations.

---

**By using this software, you acknowledge that you have read and understood this Privacy Policy.**

**Copyright © 2024-2025 Antoine Cantin**
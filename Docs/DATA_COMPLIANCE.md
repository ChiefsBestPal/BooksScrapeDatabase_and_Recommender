# Data Source Compliance Guide

**Last Updated**: September 2025

This document provides detailed guidance on complying with third-party platform Terms of Service when using BookScrapeDB_Recommends.

> [!TIP]
> This is an important document for legality and practices on data crawling,scraping,collecting and mining
> If any informations, references, samples, links, docs, etc... is out of date. Feel free to report


---

## Data Source Overview 

### PUBLICLY AVAILABLE DATA:
- Goodreads: Book metadata, user reviews, ratings, reviewer data, user profiles and followings, feeds, tags, deep book data/settings, reading lists
- Google Books: Google user reviews/insights, Bibliographic data, book metadata, cover images, links, external ref to flexible authoritative or open-source user generated
- OpenLibrary: Catalog data, subject classifications, community contributions, tags, external user generated data opensource links/platforms/community
- ISBNdb: supply chain, market pricing, editions, validation authoritative IDs and publisher/licensor, series editions, literature market data
- External sources: Independently published catalogs, attributions, indirect user contet from indepedent sites, and references
  linked from the above platforms

### API DATA (With Proper Authorization):
- Google Books API: Official access with API key and rate limiting
- OpenLibrary API: Open data initiative (public domain)
- ISBNdb API: Subscription-based access for ISBN validation

### USER DATA HANDLING:
- Reviewer identities: Processed but anonymized in outputs
- User reviews: Transformed into sentiment scores, embeddings, and statistical models
- Profile data: Aggregated for behavioral analysis, not individually identifiable
- No authentication credentials or private data accessed

### AI/ML PROCESSING:
- Large Language Models (LLMs): Used for review sentiment analysis and reader profiling
- Retrieval-Augmented Generation (RAG): Hybrid Vector+Graph embeddings for recommendations
- Natural Language Processing (NLP): Text mining on publicly available review content
- Graph Analytics: Network analysis on reading communities and influence patterns

## ⚠️ Important Disclaimer

**This guide is for informational purposes only and does NOT constitute legal advice.**

Users of this code are **solely responsible** for:
- Determining applicable laws in their jurisdiction
- Obtaining necessary permissions for their specific use case
- Ensuring compliance with platform Terms of Service
- Consulting legal counsel for production or commercial deployments

---

## 1. Goodreads

### 1.1 Terms of Service

**Official ToS**: [Goodreads Terms of Use](https://www.goodreads.com/about/terms)  
**Last Updated**: April 28, 2021  
**Owner**: Goodreads LLC (Amazon)

### 1.2 Key Restrictions for production / usage at scale from 2021 onward

Goodreads ToS Section 1 explicitly prohibits a lot of usage of scraping/mining

**What this means:**
- Automated scraping tools are explicitly prohibited without authorization
- Collection of reviews, book data, or user profiles requires permission
- Publicly visible data still subject to Terms of Service
- Commercial use requires explicit written agreements

### 1.3 Compliance Approach for This Project

**For Production/Commercial Use:**
Any production deployment or commercial use of data collection from Goodreads was/will be conducted through:
- ✅ **Explicit written agreements** obtained from Goodreads prior to data collection
- ✅ **Dated Terms of Service compliance** verified at time of data collection
- ✅ **Regulatory compliance** with applicable data protection laws
- ✅ **Small-scale compliant collection** with express permission when required

**For Educational/Research/Portfolio Use:**
Outside of production contexts, this codebase serves as:
- 📚 **Demonstration** of ETL pipeline architecture and data engineering concepts
- 🎓 **Educational resource** for learning graph analytics and recommendation systems
- 🔬 **Research tool** for academic exploration of literary network analysis
- 💼 **Portfolio showcase** of technical capabilities in data science

**Respectful Practices Implemented:**
- ✅ **robots.txt compliance**: Respects crawling directives
- ✅ **Rate limiting**: Prevents server overload (2+ second delays)
- ✅ **Transparent User-Agent**: Identifies crawler honestly
- ✅ **Incremental processing**: Minimizes redundant requests
- ✅ **No bulk redistribution**: Data transformed into aggregated insights

### 1.4 Important Clarification: Multi-Source Data

> [!IMPORTANT]  
> **User-generated content in this project is NOT exclusively from Goodreads.**

This platform aggregates data from multiple sources:

**Primary User Review Sources:**
- **Google Books**: Google user reviews and ratings (separate from Goodreads)
- **OpenLibrary**: Community-contributed reviews and annotations
- **External Catalogs**: Independent literary websites and databases linked from the above platforms
- **Public Domain Sources**: Open-source literary databases and review aggregators

**Cross-Referenced Content:**
- Goodreads, Google Books, and OpenLibrary frequently **link to external sources**
- These external platforms host user-generated content under their own Terms of Service
- Many external sites explicitly allow scraping or provide open APIs
- Cross-referencing ISBN data connects reviews across multiple platforms

**Example Data Flow:**
```
ISBN 978-0-123456-78-9 →
  ├── Goodreads: Book metadata + review counts
  ├── Google Books: API data + Google user reviews
  ├── OpenLibrary: Catalog data + community annotations
  └── External sites: Independent reviews from linked sources
```

**Result**: User review data originates from **diverse sources**, not solely Goodreads. This multi-source approach:
- Reduces dependency on any single platform
- Respects individual platform limitations
- Enriches data quality through cross-validation
- Distributes collection across compliant channels

### 1.5 Risk Assessment

| Use Case | Compliance Status | Notes |
|----------|------------------|-------|
| **Educational demonstration** | Acceptable | Non-commercial, transformative use |
| **Academic research** | Acceptable with attribution | Small-scale, proper citation |
| **Portfolio showcase** | Acceptable | Technical capability demonstration |
| **Production deployment** | Requires authorization | Must obtain explicit permission |
| **Commercial service** | Requires licensing | Written agreements mandatory |

### 1.6 Recommended Practices

**For Educational/Research Users:**
1. **Acknowledge limitations** in documentation and presentations
2. **Use synthetic data** for public demonstrations when possible
3. **Keep scale small** - collect only what's necessary for learning
4. **Cite properly** - attribute data sources in academic work
5. **Respect robots.txt** - always check and comply

**For Production/Commercial Users:**
1. **Contact Goodreads Legal**: copyright@goodreads.com
2. **Document your use case** with specific data needs
3. **Propose compliance measures** (rate limits, attribution, etc.)
4. **Obtain written permission** before deployment
5. **Review terms periodically** - Terms of Service may change

**Alternative: Official API (When Available)**
- Monitor for API reinstatement announcements
- Register for API access when/if it becomes available
- Transition from scraping to official API endpoints

---

## 2. Google Books

### 2.1 Terms of Service

**Official API Terms**: [Google Books API Terms](https://developers.google.com/books/terms)  
**Owner**: Google LLC

### 2.2 Compliance Status

✅ **Fully compliant** when using official Google Books API with proper authorization.

**Requirements:**
- Valid API key (register at [Google Cloud Console](https://console.cloud.google.com/))
- Rate limiting: Default 1,000 queries/day (adjustable with quotas)
- Proper attribution: "Powered by Google Books" or similar
- No bulk downloading of full book content (metadata only)

### 2.3 Implementation in This Project

**API Usage:**
```python
# Example compliant implementation
import requests

API_KEY = os.environ.get('GOOGLE_BOOKS_API_KEY')
RATE_LIMIT_DELAY = 0.1  # 100ms between requests

def fetch_google_books_data(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={API_KEY}"
    time.sleep(RATE_LIMIT_DELAY)
    response = requests.get(url)
    return response.json()
```

**Data Collected:**
- ✅ Book metadata (titles, authors, publishers, ISBNs)
- ✅ Descriptions and subject classifications
- ✅ Cover image URLs
- ✅ Retail/list pricing information
- ✅ **Google user reviews** (separate from Goodreads reviews)

**Google Reviews vs. Goodreads Reviews:**
- Google Books has its own user review system
- These reviews are separate from and independent of Goodreads
- Accessible via official API with proper authentication
- Subject to Google's Terms of Service, not Goodreads'

### 2.4 Best Practices

**Rate Limiting:**
```python
# Recommended delays
GOOGLE_BOOKS_DELAY = 0.1  # 100ms (well within rate limits)
```

**Caching:**
```python
# Cache API responses to minimize redundant calls
cache_file = 'google_books_cache.json'
# Reduces API usage by 95%+ on subsequent runs
```

**Attribution:**
- Include "Data from Google Books" in outputs
- Link back to Google Books when displaying book data
- Respect thumbnail usage guidelines

---

## 3. OpenLibrary

### 3.1 Terms of Service

**Official ToS**: [OpenLibrary Terms](https://openlibrary.org/terms)  
**Owner**: Internet Archive (Non-profit)
**Data License**: Open data initiative - public domain where applicable

### 3.2 Compliance Status

✅ **Fully compliant** - OpenLibrary explicitly supports open data access.

**Key Advantages:**
- No API key required for basic access
- Generous rate limits for non-commercial use
- Encourages data reuse for educational/research purposes
- Provides bulk data dumps for large-scale projects

### 3.3 Implementation in This Project

**API Access:**
```python
# OpenLibrary API - No authentication required
url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
response = requests.get(url)
```

**Data Collected:**
- ✅ Catalog metadata (titles, authors, editions)
- ✅ Subject classifications and Library of Congress data
- ✅ Community-contributed content
- ✅ Links to external sources (other libraries, databases)
- ✅ **Community reviews and annotations** (separate user base from Goodreads)

**External Sources via OpenLibrary:**
- OpenLibrary links to **hundreds of external catalogs and databases**
- These linked sources often have their own user-generated content
- Cross-referencing ISBNs discovers reviews on independent platforms
- Each external source subject to its own Terms of Service

### 3.4 Best Practices

**Rate Limiting:**
```python
OPENLIBRARY_DELAY = 1.0  # 1 second (respectful, not required)
```

**Attribution:**
- Credit Internet Archive/OpenLibrary in documentation
- Link back to OpenLibrary records when appropriate
- Consider donating to support the non-profit mission

**Bulk Data Access:**
- For large projects, use official data dumps: https://openlibrary.org/developers/dumps
- More efficient and respectful than scraping

---

## 4. ISBNdb

### 4.1 Terms of Service

**Official ToS**: [ISBNdb Terms](https://isbndb.com/terms)  
**Owner**: ISBNdb.com

### 4.2 Compliance Status

✅ **Requires API subscription** for access.

**Access Tiers:**
- **Free Tier**: 100 requests/day (educational use)
- **Paid Tiers**: Higher limits + commercial rights
- **Enterprise**: Bulk access with custom agreements

### 4.3 Implementation in This Project

**API Usage:**
```python
API_KEY = os.environ.get('ISBNDB_API_KEY')
headers = {'Authorization': API_KEY}
url = f"https://api2.isbndb.com/book/{isbn}"
response = requests.get(url, headers=headers)
```

**Data Collected:**
- ✅ ISBN validation and edition tracking
- ✅ Pricing statistics (retail/list prices)
- ✅ Publisher information
- ✅ Format and availability data

### 4.4 Best Practices

**Subscription Management:**
- Monitor daily quota usage
- Implement caching to minimize API calls
- Upgrade tier if approaching limits

**Commercial Use:**
- Free tier: Educational/research only
- Commercial deployment: Requires paid subscription
- Review terms for redistribution rights

---

## 5. External Catalogs & Independent Sources

### 5.1 Overview

**Important**: A significant portion of user-generated content in this project comes from **external sources** linked by primary platforms.

**How External Sources Are Discovered:**
1. **ISBN Cross-Referencing**: Same ISBN appears across multiple platforms
2. **Platform Links**: Goodreads/Google Books/OpenLibrary link to external catalogs
3. **Independent Databases**: Literary websites, review aggregators, library systems
4. **Open-Source Platforms**: Community-driven book databases with permissive licenses

### 5.2 Examples of External Sources

**Academic & Library Systems:**
- WorldCat (OCLC)
- Library of Congress
- University library catalogs
- Digital library consortia

**Independent Review Platforms:**
- LibraryThing
- BookLikes
- Litsy
- Shelfari (archived)

**Public Domain & Open Data:**
- Project Gutenberg
- HathiTrust
- Archive.org literary collections
- Wikipedia book articles

**Commercial Aggregators:**
- Amazon (reviews via API)
- Barnes & Noble
- Kobo
- Indie bookseller sites

### 5.3 Compliance Approach

**For Each External Source:**

1. **Verify Terms of Service**: Check robots.txt and ToS before scraping
2. **Respect Rate Limits**: Implement appropriate delays
3. **Provide Attribution**: Credit original sources in documentation
4. **Use APIs When Available**: Prefer official APIs over scraping
5. **Document Permissions**: Maintain records of ToS compliance

**Example Compliance Check:**
```python
# Before scraping any external source
def check_compliance(domain):
    # 1. Check robots.txt
    robots_url = f"https://{domain}/robots.txt"
    
    # 2. Verify ToS allows data collection
    tos_url = f"https://{domain}/terms"
    
    # 3. Implement appropriate rate limiting
    DELAY = 2.0  # Conservative default
    
    # 4. Use transparent User-Agent
    USER_AGENT = "BookScrapeDB/1.0 Educational Research"
```

### 5.4 Multi-Source Data Aggregation

**Key Point**: By aggregating user reviews from **multiple independent sources**, this project:

✅ **Reduces reliance** on any single platform  
✅ **Respects individual platform limits** by distributing collection  
✅ **Enriches data quality** through cross-validation  
✅ **Mitigates compliance risk** by diversifying sources  
✅ **Provides attribution** to original content creators  

**Data Provenance Tracking:**
```python
# Each review tagged with source platform
review = {
    'text': 'Review content...',
    'rating': 4.5,
    'source': 'google_books',  # or 'openlibrary', 'external_catalog', etc.
    'source_url': 'https://...',
    'collected_date': '2025-01-15'
}
```

---

## 6. General Compliance Best Practices

### 6.1 Rate Limiting Standards

**Recommended Delays Between Requests:**
```python
# Platform-specific delays (in seconds)
RATE_LIMITS = {
    'goodreads': 2.0,        # Conservative (educational use only)
    'google_books': 0.1,     # Within API rate limits
    'openlibrary': 1.0,      # Respectful, not strictly required
    'isbndb': 0.5,           # API subscription allows faster
    'external_default': 2.0  # Conservative for unknown sources
}
```

### 6.2 robots.txt Compliance

**Always check before scraping:**
```python
from urllib.robotparser import RobotFileParser

def can_fetch(url):
    rp = RobotFileParser()
    rp.set_url(f"{url.split('/')[0]}//robots.txt")
    rp.read()
    return rp.can_fetch("*", url)
```

**Common robots.txt Examples:**
- **Goodreads**: Restricts most crawlers (respect these restrictions)
- **Google Books**: Allows API access, restricts bulk scraping
- **OpenLibrary**: Generally permissive for non-commercial use

### 6.3 User-Agent Identification

**Use transparent, identifiable User-Agent strings:**
```python
USER_AGENT = (
    "BookScrapeDB/1.0 "
    "(Educational Research Project; "
    "+https://github.com/ChiefsBestPal/BooksScrapeDatabase_and_Recommender; "
    "contact@example.com)"
)
```

**Why this matters:**
- ✅ Allows platforms to contact you if issues arise
- ✅ Demonstrates good faith and transparency
- ✅ Distinguishes your crawler from malicious bots
- ✅ Enables platform-specific rate limiting

### 6.4 Data Anonymization

**Protect user privacy in all outputs:**
```python
# Anonymize reviewer identities
reviewer_hash = hashlib.sha256(username.encode()).hexdigest()[:12]

# Never export mappings between usernames and IDs
# Store only aggregated statistics
```

### 6.5 Attribution Requirements

**Always credit data sources:**
```markdown
## Data Sources
This project uses data from:
- Goodreads™ (deep book metadata/details, author/community/reviewers content and profiles, lists/feeds)
- Google Books™ (google users, API data and user reviews)
- OpenLibrary™ (catalog data and community content)
- ISBNdb™ (ISBN validation, market reltated data)
- [List external sources used]

All trademarks are property of their respective owners.
```

---

## 7. Production Deployment Checklist

### 7.1 Before Production Use

**Legal Requirements:**
- [ ] Review all applicable platform Terms of Service
- [ ] Obtain explicit written permissions where required
- [ ] Document compliance measures in writing
- [ ] Consult legal counsel for your specific jurisdiction
- [ ] Verify GDPR/CCPA compliance if applicable

**Technical Requirements:**
- [ ] Implement robust rate limiting
- [ ] Set up monitoring and alerting for API issues
- [ ] Configure secure credential storage (not in code!)
- [ ] Implement data anonymization in all outputs
- [ ] Set up logging for compliance auditing

**Documentation Requirements:**
- [ ] Create internal compliance documentation
- [ ] Document data sources and permissions obtained
- [ ] Maintain records of Terms of Service versions at time of collection
- [ ] Establish data retention and deletion policies
- [ ] Prepare user-facing privacy policy

### 7.2 Ongoing Compliance

**Regular Reviews:**
- Review platform Terms of Service quarterly for changes
- Monitor for API deprecation announcements
- Update rate limits if platform policies change
- Audit data collection practices annually

**Incident Response:**
- Prepare process for cease-and-desist responses
- Document escalation procedures
- Maintain legal counsel contact information
- Have data deletion procedures ready

---

## 8. Alternatives to Scraping

### 8.1 Official APIs (Preferred)

**When available, always prefer official APIs:**
- ✅ **Google Books API**: Fully supported and compliant
- ✅ **OpenLibrary API**: Open data, no restrictions
- ✅ **ISBNdb API**: Commercial options available
- ⚠️ **Goodreads API**: Deprecated (2021), monitor for reinstatement, alternative platforms and/or obtain explicite agreement/permission with copyrights teams at Goodreads or Amazon LLCs

### 8.2 Data Partnerships

**For commercial projects, consider:**
- Direct partnerships with platforms
- Licensed data access agreements
- Data sharing arrangements
- Revenue-sharing models

### 8.3 Synthetic Data

**For demonstrations and testing:**
- Generate synthetic book/review data
- Use public domain literature (Project Gutenberg)
- Create representative sample datasets
- Anonymize and aggregate real data

### 8.4 User-Contributed Data

**Alternative approach:**
- Build opt-in data contribution system
- Allow users to import their own reading data
- Goodreads provides data export tools (users can share voluntarily)
- This approach is fully compliant with all ToS

---

## 9. Academic & Research Use

### 9.1 Academic Exemptions

**Many jurisdictions provide research exemptions, but these are limited:**

**What's typically allowed:**
- Small-scale collection for academic research
- Proper citation and attribution
- Non-commercial publication of findings
- Transformative use (analysis, not redistribution)

**What's still restricted:**
- Large-scale commercial use
- Bulk redistribution of data
- Bypassing technical protection measures
- Violating explicit Terms of Service

**Important**: Academic exemptions vary by jurisdiction and do not override contractual ToS agreements in all cases.

### 9.2 Institutional Review

**For academic projects:**
- Consult your institution's IRB (Institutional Review Board)
- Review data ethics policies
- Obtain necessary approvals for human subjects research
- Document compliance with institutional guidelines

### 9.3 Publication Guidelines

**When publishing research using this data:**
- ✅ Cite all data sources properly
- ✅ Describe data collection methodology
- ✅ Acknowledge any Terms of Service considerations
- ✅ Share aggregated findings, not raw data
- ✅ Make anonymized datasets available when possible (if permitted)

---

## 10. Updates & Changes

### 10.1 Monitoring Platform Changes

**Stay informed about:**
- Terms of Service updates (check quarterly)
- API deprecations or new releases
- Rate limit changes
- Enforcement policy updates

**Resources:**
- Platform developer blogs
- API documentation change logs
- Legal/compliance newsletters
- GitHub security advisories

### 10.2 This Document

**This compliance guide is updated as:**
- Platform terms change
- New data sources are added
- Compliance best practices evolve
- User feedback identifies gaps

**Check the "Last Updated" date regularly.**

---

## 11. Contact & Questions

### 11.1 Platform-Specific Contacts

**For permissions or clarifications:**

- **Goodreads**: copyright@goodreads.com
- **Google Books**: See [Google Books Partner Program](https://books.google.com/partner/)
- **OpenLibrary**: See [OpenLibrary Contact](https://openlibrary.org/contact)
- **ISBNdb**: See [ISBNdb Support](https://isbndb.com/contact)

### 11.2 Project Maintainer

**For questions about this compliance guide:**
- Open a GitHub issue
- Contact @ChiefsBestPal via GitHub
- See ```SECURITY.md``` for security concerns

---

## 12. Legal Disclaimer

**IMPORTANT: This document does NOT constitute legal advice.**

The information provided is for educational purposes and represents the maintainer's understanding of compliance requirements as of the last update date.

**You are responsible for:**
- ✅ Conducting your own legal analysis
- ✅ Consulting qualified legal counsel
- ✅ Ensuring compliance in your specific jurisdiction
- ✅ Obtaining necessary permissions for your use case
- ✅ Monitoring for changes in applicable laws and terms

**The author makes NO warranties** about the accuracy, completeness, or legal sufficiency of this guidance.

---

**By using this software, you acknowledge that you have read this compliance guide and accept sole responsibility for ensuring your use complies with all applicable laws and Terms of Service.**

**Copyright © 2024-2025 Antoine Cantin**
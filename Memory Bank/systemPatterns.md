# System Patterns

## Architecture
- Two-phase scraping approach
  1. Main page scraping (guaranteed data)
  2. Individual page scraping (best effort)
- MongoDB storage with upsert functionality
- Scheduled execution with configurable intervals

## Technical Decisions
- Selenium for dynamic content handling
- BeautifulSoup for HTML parsing
- MongoDB for flexible data storage
- Python scheduler for automated updates

## Component Relationships
```mermaid
flowchart TD
    A[Main Scraper] --> B[MongoDB Storage]
    A --> C[Individual Page Scraper]
    C --> B
    D[Scheduler] --> A
